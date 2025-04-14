import sys, os
import subprocess as sp
import gzip
import io
import time
import queue
import threading
import multiprocessing
from multiprocessing import shared_memory, Pool
import struct
import traceback
import signal
import math
import argparse

parser = argparse.ArgumentParser(description="Retrieve the top N poses from docking results")
parser.add_argument("dockresults_path", type=str, help="Can be either a directory containing docking results, or a file where each line points to a docking results file.")
parser.add_argument("-n", dest='nposes', type=int, default=150000, help="How many top poses to retrieve, default of 150000")
parser.add_argument("-o", dest='outprefix', type=str, default="top_poses", help="Output file prefix. Each run will produce two files, a mol2.gz containing pose data, and a .scores file containing relevant score information. Default is \"top_poses\"")
parser.add_argument("-j", dest='nprocesses', type=int, default=8, help="How many processes should be dedicated to this run, default is 8.")
parser.add_argument("--id-file", dest='input_id_file', type=str, default=None, help="Only retrieve poses matching ids specified in an external file.")
parser.add_argument("--quiet", action='store_const', const=True, default=False)

args = parser.parse_args()

dockresults_path = args.dockresults_path
output_file = args.outprefix + '.mol2.gz'
scores_file = args.outprefix + '.scores'
nprocesses = args.nprocesses
input_id_file = args.input_id_file
max_heap_size = args.nposes
quiet = args.quiet

def get_to_search(dockresults_path):

    if os.path.isfile(dockresults_path):
        with open(dockresults_path, 'r') as dockresults_path_f:
            for line in dockresults_path_f:
                yield line.strip()
    elif os.path.isdir(dockresults_path):
        with sp.Popen(["find", "-L", dockresults_path, "-type", "f", "-name", "test.mol2.gz*"], stdout=sp.PIPE) as find_dockresults:
            for line in find_dockresults.stdout:
                yield line.decode('utf-8').strip()
    else:
        print("Supplied dock results path {} cannot be found!".format(dockresults_path))
        sys.exit(1)

class MinHeap:

    def __init__(self, maxsize=10000):
        self.maxsize = maxsize
        self.size = 0
        self.heap = [[None, 0, 0, ''] for i in range(maxsize+1)] # element object, element value, element index, element name
        self.heap[0][1] = float('inf') # set root element value to maximum. It should not get popped or replaced
        self.nameMap = {}

    # average time complexity: O(log2(n))
    def insert(self, element, name, value):
        self.size += 1

        current = self.size
        popped = self.heap[current]
        parent = self.size // 2
        parentval = self.heap[parent][1]


        if not self.size == 1:
            while value > parentval:
                self.heap[current] = self.heap[parent]
                self.heap[current][2] = current
                current = parent
                parent = current // 2
                parentval = self.heap[parent][1]

        
        popped[0] = element
        popped[1] = value
        popped[2] = current
        popped[3] = name
        self.heap[current] = popped
        self.nameMap[name] = self.heap[current]

    # average time complexity: O(log2(n))
    def remove_insert(self, elem, name, value):
        del self.nameMap[self.heap[1][3]]

        self.update(1, elem, name, value)

    # due to the additional requirements of top_poses, we also maintain a hash table to keep track of element names
    # we only allow one element per name
    def update_by_name(self, elem, name, value):
        to_update = self.nameMap.get(name)

        if not to_update:
            if self.size < self.maxsize:
                self.insert(elem, name, value)
                return
            else:
                self.remove_insert(elem, name, value)
                return

        elif value > to_update[1]:
            return

        update_idx = to_update[2]

        self.update(update_idx, elem, name, value)

    def update(self, index, elem, name, value):

        popped = self.heap[index] # make sure to keep track of the original item we are updating
        # it can be easy to get lost in a forest of pointers...

        # if you want an explanation for the minheap algorithm, google it
        pos = index
        lastparent = self.size // 2
        while pos < lastparent:
            lchild = 2 * pos
            rchild = 2 * pos + 1

            lval = self.heap[lchild][1]
            rval = self.heap[rchild][1]

            maxchild, maxval = (lchild, lval) if lval > rval else (rchild, rval)

            if value > maxval:
                break
            else:
                self.heap[pos] = self.heap[maxchild]
                self.heap[pos][2] = pos
                pos = maxchild

        # if tree contains even number of nodes, the last parent will have just one (left) node
        # if our path down the tree takes us to this parent node, we will miss it
        # deal with this case outside of our main loop so we don't need to perform the conditionals every time
        if pos == lastparent:
            lchild = 2 * pos
            rchild = 2 * pos + 1
            if (self.size % 2) == 0:
                lval = self.heap[lchild][1]
                if not value > lval:
                    self.heap[pos] = self.heap[lchild]
                    self.heap[pos][2] = pos
                    pos = lchild
            else:
                lval = self.heap[lchild][1]
                rval = self.heap[rchild][1]
                maxchild, maxval = (lchild, lval) if lval > rval else (rchild, rval)

                if value > maxval:
                    pass
                else:
                    self.heap[pos] = self.heap[maxchild]
                    self.heap[pos][2] = pos
                    pos = maxchild

        # update the original item and place at correct position in the heap
        popped[0] = elem
        popped[1] = value
        popped[2] = pos
        popped[3] = name
        self.heap[pos] = popped
        self.nameMap[name] = self.heap[pos]

    def minvalue(self):
        return self.heap[1][1]

class BufferedLineReader:

    def __init__(self, filename, delimeter='\n', bufsize=1024*1024*32):
        self.bufsize = bufsize
        if '.gz' in filename:
            try:
                self.file = gzip.open(filename, 'rt')
            except:
                self.file = open(filename, 'r')
        else:
            self.file = open(filename, 'r')
        self.buf = None
        self.delimeter = delimeter
        self.delimsize = len(delimeter)
        self.__readbuf()

    def __readbuf(self):
        del self.buf
        self.buf = self.file.read(self.bufsize)
        self.buflen = len(self.buf)
        self.lines = self.buf.split(self.delimeter) # the built-in 'split' function is very fast and much better than a while loop to detect newlines
        self.nlines = len(self.lines)
        self.partial = False if not self.buf else self.buf[-self.delimsize] != self.delimeter
        self.lineidx = 0

    def readline(self):
        line = self.lines[self.lineidx]

        if self.lineidx == (self.nlines - 1):
            self.nlines = 1
            if not self.partial:
                self.__readbuf()
                return line
            while self.partial and self.nlines == 1:
                self.__readbuf()
                line += self.lines[0]
                self.lineidx = 1
            return line

        self.lineidx += 1
        return line

# Used to create a fully annotated mol2 structure, for use in writing out to .scores
class Mol2Data:

    dataterms = {
        "Name" : (0, str),
        "Number" : (1, int),
        "FlexRecCode" : (2, int),
        "Matchnum" : (3, int),
        "Setnum" : (4, int),
        "Rank" : (5, int),
        "Ligand Charge" : (6, float), # charge is printed out as a float for whatever reason
        "Electrostatic" : (7, float),
        "Gist": (8, float),
        "Van der Waals": (9, float),
        "Ligand Polar Desolv" : (10, float),
        "Ligand Apolar Desolv" : (11, float),
        "Receptor Desolvation" : (12, float),
        "Receptor Hydrophobic" : (13, float),
        "Total Strain" : (14, float),
        "Max Strain" : (15, float),
        "Total Energy" : (16, float)
    }

    def __init__(self, data):
        self.data = data
        self.items = [None for i in range(17)]

        for line in self.data.decode('utf-8').split('\n'):
            if line.startswith("##########"):

                item_name = line[10:31].strip()
                item_data = line[32:].strip()
                item_props = Mol2Data.dataterms.get(item_name)
                if item_props:
                    item_idx, item_type = item_props
                    self.items[item_idx] = item_type(item_data)

            else:
                break

    def get_name(self):
         return self.items[0]

    def get_total_energy(self):
         return self.items[16]

class SharedMemoryQueue_Mol2Data:

    def __init__(self, bufsize=1024*1024*64, maxitems=500): # 32 MB of designated space default, 500 items
        # if those 500 items exceed 32 MB of space, an error will be thrown (or maybe not...? regardless something bad will happen)
        # for mol2 data, 32 MB for 500 items is overkill, but a price we can pay quite easily
        self.bufsize = bufsize
        self.maxitems = maxitems
        self.modlock = multiprocessing.Lock()
        self.getlock = multiprocessing.Lock()
        self.putlock = multiprocessing.Lock()
        self.canget  = multiprocessing.Event()
        self.canput  = multiprocessing.Event()
        self.shared_mem = shared_memory.SharedMemory(create=True, size=bufsize)
        self.shared_buffer = self.shared_mem.buf
        self.starting_idx = 12

        self.__set_putidx(self.starting_idx)
        self.__set_getidx(self.starting_idx)
        self.__set_nitems(0)

    def __set_putidx(self, val):
        self.shared_buffer[0:4] = (val).to_bytes(4, 'big')

    def __get_putidx(self):
        return int.from_bytes(self.shared_buffer[0:4], 'big')

    def __set_getidx(self, val):
        self.shared_buffer[4:8] = (val).to_bytes(4, 'big')

    def __get_getidx(self):
        return int.from_bytes(self.shared_buffer[4:8], 'big')
       
    def __set_nitems(self, val): # should only call at the very start to set the initial value
        self.shared_buffer[8:12] = (val).to_bytes(4, 'big')
 
    def __inc_nitems(self, inc_val):
        self.modlock.acquire()
        curr_val = int.from_bytes(self.shared_buffer[8:12], 'big')
        self.shared_buffer[8:12] = (curr_val+inc_val).to_bytes(4, 'big')
        self.modlock.release()

    def __get_nitems_unsafe(self):
        return int.from_bytes(self.shared_buffer[8:12], 'big')

    def __about_to_be_full(self, nbytes):
        putidx = self.__get_putidx()
        getidx = self.__get_getidx()
        return putidx + nbytes > getidx and putidx < getidx


    def put(self, buff, enrg, name, timeout=None):

        if not self.putlock.acquire(True, timeout):
            raise NameError("put timeout reached!")
            return

        # wait for queue to not be full
        t_start = time.time()
        while self.__get_nitems_unsafe() == self.maxitems:
            t_elapsed = time.time() - t_start
            if t_elapsed > timeout:
                raise NameError("put timeout reached!")
                return

        putidx = self.__get_putidx()

        total_energy_bytes  = struct.pack('f', enrg)
        mol_name_bytes      = "{:64s}".format(name).encode('utf-8')
        buffer_bytes        = buff.encode('utf-8')
        buffer_size         = len(buffer_bytes)
        buffer_size_bytes   = int.to_bytes(buffer_size, 4, 'big')

        nbytes_to_write = buffer_size + 72
        
        if (putidx + nbytes_to_write + 4) >= self.bufsize: # the +4 is counting the 4 bytes needed to signal the end of the usable buffer
            self.shared_buffer[putidx:putidx+4] = int.to_bytes(0xffffffff, 4, 'big', signed=False) # signal the end of the usable buffer
            putidx = self.starting_idx

        self.shared_buffer[putidx:putidx+4]                 = buffer_size_bytes
        self.shared_buffer[putidx+4:putidx+68]              = mol_name_bytes
        self.shared_buffer[putidx+68:putidx+72]             = total_energy_bytes
        self.shared_buffer[putidx+72:putidx+buffer_size+72] = buffer_bytes

        self.__set_putidx(putidx + nbytes_to_write) # 72 bytes of constant data plus variable buffer size
        self.__inc_nitems(1) # nitems is an atomic integer

        self.putlock.release()

    def get(self, timeout=None):

        if not self.getlock.acquire(True, timeout):
            return None

        # wait for queue to not be empty
        t_start = time.time()
        while self.__get_nitems_unsafe() == 0:
            t_elapsed = time.time() - t_start
            if t_elapsed > timeout:
                return None

        getidx = self.__get_getidx()

        buffer_size  = int.from_bytes(self.shared_buffer[getidx:getidx+4], 'big', signed=False)
        if buffer_size == 0xffffffff: # we've reached the end of the usable buffer. roll back to index 0
            self.__set_getidx(self.starting_idx)
            getidx = self.starting_idx
            buffer_size = int.from_bytes(self.shared_buffer[getidx:getidx+4], 'big', signed=False)
        
        nbytes_to_read  = buffer_size + 72
        mol_name_bts    = bytes(self.shared_buffer[getidx+4:getidx+68])
        mol_name        = mol_name_bts.decode('utf-8').strip()
        total_energy    = struct.unpack('f', self.shared_buffer[getidx+68:getidx+72])[0] # for some reason struct.unpack creates a tuple instaed of a float
        buffer_bytes    = bytes(self.shared_buffer[getidx+72:getidx+72+buffer_size])

        self.__inc_nitems(-1)
        self.__set_getidx(getidx + nbytes_to_read)

        self.getlock.release()

        to_return = (buffer_bytes, mol_name, total_energy)
        return to_return

    def release(self):
        self.shared_mem.close()
        self.shared_mem.unlink()

# Main Function for producer threads
# The main function of the producer thread is to read in files and produce the data to be consumed by the main thread
# Disk I/O is faster when done on multiple threads, which is the producer's main purpose, but not it's only one
# Only one thread capable of interfacing with the heap, so it is best to offload as much work as possible to the producer threads, which are more numerous. 
# Producers are tasked not just with reading in data, but also annotating it for the heap thread, with necessary information like molecule name & total energy.
# This seems small, but actually saves an incredible amount of time. 
# Once poses have been sorted through according to name & energy, the main thread will further annotate the score data and write it out to the .scores file
def posedata_producer(processing_queue, filenames_queue, input_done_semaphore, ppid, quiet):
    print("producer started")

    stop = False
    def donothing(signum, frame):
        nonlocal stop
        stop=True
        pass

    signal.signal(signal.SIGINT, donothing)

    def finish():
        if not input_done_semaphore.acquire(False, None):
            sp.call(["kill", "-2", str(ppid)])

    #mol_delimeter = "##########                 Name"
    mol_delimeter = '\n'
    while not stop:
        try:
            posesfile = filenames_queue.get(True, timeout=2)
        except:
            break
        try:

            # fancy custom line reader class, unsure if necessary
            reader = BufferedLineReader(posesfile, delimeter=mol_delimeter)
            buff = ""
            enrg = 99999
            if not quiet: print(posesfile)

        except:
            traceback.print_exc()
            print("error reading in {}, continuing".format(posesfile))
            continue

        error = 0

        line = reader.readline()
        while reader.buflen > 0:
            # each mol2 in DOCK output has the following string in it's header
            if line.startswith("##########                 Name"):
                if buff: # only produce data if we have an existing buffer, i.e don't do this on the first loop
                    # produce this data to the queue
                    try:
                        processing_queue.put(buff, enrg, name, 60)
                    except:
                        print("caught timeout error:")
                        traceback.print_exc()
                        finish()
                        return
                    buff = ""
                    enrg = 99999
                name = line.split(':')[1].strip()
            # the heap thread compares on total energy score, so we gather this information from the mol2
            elif line.startswith("##########         Total Energy"):
                enrg = float(line.split(':')[1].strip())

            buff += line + '\n'
            try:
                line = reader.readline()
            except:
                print("encountered error while reading {}. Stopping read.".format(posesfile))
                error = 1
                break

        if error == 0 and not (buff == ""):
            try:
                processing_queue.put(buff, enrg, name, 60)
            except:
                traceback.print_exc()
                finish()
                return

    print("producer done")
    finish()
        
def filenames_producer(filenames_queue, path_enum):
    def donothing(signum, frame):
        pass
    print("filename producer started")
    for path in path_enum:
        filenames_queue.put(path)
    print("done producing filenames!")

if not quiet: print("allocating resources...")
heap = MinHeap(max_heap_size)
modlock, getlock, putlock = (multiprocessing.Lock() for i in range(3))
filenames_queue = multiprocessing.Queue()
processing_queue = SharedMemoryQueue_Mol2Data()
#processing_queue = multiprocessing.Queue(maxsize=500) # useful for debugging. Works, but is slow as ****
filenames_producer(filenames_queue, get_to_search(dockresults_path))

posedata_producer_pool = [None for i in range(nprocesses)]

ppid = os.getpid()
done_with_input_semaphore = multiprocessing.Semaphore(nprocesses-1)

for i in range(nprocesses):
    if not quiet: print("launching {}".format(i))
    posedata_producer_pool[i] = multiprocessing.Process(target=posedata_producer, args=(processing_queue, filenames_queue, done_with_input_semaphore, ppid, quiet))
    posedata_producer_pool[i].start()
if not quiet: print("done launching")

hit_max = False

i = 0

time_total_start = time.time()
receive_data_time_total = 0
heap_insert_time_total  = 0

stop = False

def int_handler(signum, frame):
    global stop
    print("received interrupt!")
    stop = True

signal.signal(signal.SIGINT, int_handler)

allowed_ids = {}
if input_id_file:
    with open(input_id_file, 'r') as input_ids:
        for line in input_ids:
            molid = line.split()[0]
            allowed_ids[molid] = True

print("starting...")
started = False

# instead of using one timeout value, we have a small timeout that we repeat through multiple times to a limit of maxtimeout
# this makes the main thread more responsive when we have gone through all input. The main thread will get stuck in a
# timeout if the "all done" interrupt signal comes while main execution is blocking elsewhere.
currtimeout = 0
maxtimeout = 30
while True:

    if (i % max_heap_size) == 0 and i != 0 and not quiet:
        time_total = (time.time() - time_total_start)
        time_total_start = time.time()
        print("poses: {}".format(i))
        print("time spent receiving data: {:15f}".format(receive_data_time_total))
        print("time spent insert to heap: {:15f}".format(heap_insert_time_total))
        print("pps:                       {:15f}".format(max_heap_size / time_total))
        receive_data_time_total = 0
        heap_insert_time_total = 0

    receive_data_time = time.time()

    # get a pose from the producer queue
    pose = processing_queue.get(timeout=1)

    receive_data_time = time.time() - receive_data_time
    receive_data_time_total += receive_data_time

    if not pose:
        if stop: # final producer thread to finish will signal us when all input has been processed
            print("received all input!")
            break
        currtimeout += 1
        print("short timeout reached while retrieving pose... trying again! curr={}".format(currtimeout))
        if currtimeout >= maxtimeout:
            print("timed out while trying to get data, something has gone wrong")
            break
        continue
    else:
        currtimeout = 0

    # gather name, energy, and data for the pose
    pose_data = pose[0]
    pose_name = pose[1]
    pose_enrg = pose[2]

    if input_id_file and not allowed_ids.get(pose_name):
        i += 1
        continue

    if not started:
        print("started receiving poses!")
        started = True

    heap_insert_time = time.time()

    # update heap with pose
    # if the heap is full and the pose energy is greater than the heap maximum, the pose will be thrown away
    # if the heap is full and pose energy is less than the maximum, the maximum energy pose in the heap will be thrown away with the new pose taking its spot
    # if the heap is not full the pose will be inserted to the heap
    heap.update_by_name(pose_data, pose_name, pose_enrg)

    heap_insert_time = time.time() - heap_insert_time
    heap_insert_time_total += heap_insert_time

    i += 1

if not quiet: print("joining threads...")
for process in posedata_producer_pool:
    try:
        process.join(timeout=10) 
    except:
        process.terminate()

processing_queue.release()

print("done processing! writing out...")

data_index = sorted([(i, heap.heap[i][1]) for i in range(1, heap.size)], key=lambda m:m[1])
mol2_sorted = [Mol2Data(heap.heap[d_idx[0]][0]) for d_idx in data_index]

with gzip.open(output_file, 'w') as outfile:

    i = 0
    for mol in mol2_sorted:

        outfile.write(mol.data)
        if i % 100 == 0:
            print(i, '/', heap.size, end='\r')
        i += 1

with open(scores_file, 'w') as scorefile:

    headerstr = '|'.join([k for k in Mol2Data.dataterms.keys()])
    scorefile.write(headerstr + '\n')

    for mol in mol2_sorted:

        itemstr = '\t'.join([str(itm) for itm in mol.items])
        scorefile.write(itemstr + '\n')

print()
