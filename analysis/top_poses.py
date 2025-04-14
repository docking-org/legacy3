import sys, os
import subprocess as sp
import gzip
import io
import time
import queue
import multiprocessing

if len(sys.argv) == 0:
    print("usage: top_poses.py [dock_results_path] [[output_poses_filename]]")
    sys.exit(0)

dockresults_path = sys.argv[1]
output_file = "top_poses.mol2.gz" if len(sys.argv) <= 2 else sys.argv[2]

def get_to_search(dockresults_path):

    if os.path.isfile(dockresults_path):
        with open(dockresults_path, 'r') as dockresults_path_f:
            for line in dockresults_path_f:
                yield line.strip()
                #to_search.append(line.strip())
    elif os.path.isdir(dockresults_path):
        with sp.Popen(["find", "-L", dockresults_path, "-type", "f", "-name", "test.mol2.gz.*"], stdout=sp.PIPE) as find_dockresults:
            for line in find_dockresults.stdout:
                yield line.decode('utf-8').strip()
                #to_search.append(line.strip().decode('utf-8'))
    else:
        print(("Supplied dock results path {} cannot be found!".format(dockresults_path)))
        sys.exit(1)

class MinHeap:

    def __init__(self, maxsize=10000, comparator=lambda x, y:x < y):
        self.maxsize = maxsize
        self.comparator = comparator
        self.size = 0
        self.heap = [None for i in range(maxsize+1)]

    def __swap(self, i, j):
        tmp = self.heap[i]
        self.heap[i] = self.heap[j]
        self.heap[j] = tmp

    # best case: O(1)
    # worst case: O(log2(n))
    def insert(self, element):
        self.size += 1
        self.heap[self.size] = element
        if self.size == 1:
            self.heap[0] = element
            return

        current = self.size
        parent = self.size // 2

        while self.comparator(self.heap[current], self.heap[parent]):
            self.__swap(current, parent)
            current = parent
            parent = current // 2

        self.heap[0] = self.heap[1]

    # best case: O(1)
    # worst case: O(log2(n))
    def remove_insert(self, elem):
        popped = self.heap[1]
        self.heap[1] = elem

        pos = 1
        while pos < (self.size // 2):
            lchild = 2 * pos
            rchild = 2 * pos + 1

            if self.comparator(self.heap[pos], self.heap[rchild]) and self.comparator(self.heap[pos], self.heap[lchild]):
                break

            if self.comparator(self.heap[lchild], self.heap[rchild]):
                self.__swap(pos, lchild)
                pos = lchild
            else:
                self.__swap(pos, rchild)
                pos = rchild

        self.heap[0] = self.heap[1]
        return popped

    def minvalue(self):
        return self.heap[1]

class BufferedLineReader:

    def __init__(self, filename, bufsize=1024*1024):
        self.bufsize = bufsize
        if '.gz' in filename:
            try:
                self.file = gzip.open(filename, 'rt')
            except:
                self.file = open(filename, 'r')
        else:
            self.file = open(filename, 'r')
        self.partial_line = None
        self.buf = None
        self.__readbuf()

    def __readbuf(self):
        del self.buf
        self.buf = self.file.read(self.bufsize)
        self.bufpos = 0
        self.buflen = len(self.buf)

    def readline(self):
        start=self.bufpos
        while self.bufpos < self.buflen and self.buf[self.bufpos] != '\n':
            self.bufpos += 1
        if self.bufpos == self.buflen: # we reached the end of the buffer without finding a newline
            if not self.buf:
                return '' # avoid an infinite recursive loop if buf is empty
            partial_line = self.buf[start:self.bufpos]
            self.__readbuf()
            full_line = partial_line + self.readline() # bet you didn't expect to see recursion in a readline function!
            # if this function is recursing more than once then you're dealing with some monster lines (or a very small buffer)
            return full_line
        self.bufpos += 1
        return self.buf[start:self.bufpos]

class Mol2Data:

    def __init__(self, data, total_energy, name):
        #bio = io.BytesIO()
        #gzipper = gzip.GzipFile(mode='wb', fileobj=bio)
        #gzipper.write(data.encode('utf-8'))
        #self.buf = bio.getbuffer() # store the buffer as gzipped data. Lower memory footprint this way
        # just kidding. Can't seem to get this to work- not that I mind, gzipping small files seems inefficient
        self.buf = data.encode('utf-8')
        self.total_energy = total_energy
        self.name = name

def posedata_producer(processing_queue, path_enum):

    for posesfile in path_enum:
        try:
            reader = BufferedLineReader(posesfile)
            buff = ""
            enrg = 99999
            name = ""

            line = reader.readline()
        except:
            print(("encountered error while trying to open {}. Skipping!".format(posesfile)))
            return

        error = 0
        processing_queue.put(0)

        while line:
            if line.startswith("##########                 Name"):
                if buff:
                    processing_queue.put(Mol2Data(buff, enrg, name))
                    #yield Mol2Data(buff, enrg, name)
                    #poses.append(Mol2Data(buff, enrg, name))
                    buff = ""
                    enrg = 99999
                name = line.split(':')[1].strip()
            elif line.startswith("##########         Total Energy"):
                enrg = float(line.split(':')[1].strip())

            buff += line
            try:
                line = reader.readline()
            except:
                print(("encountered error while reading {}. Stopping read.".format(posesfile)))
                error = 1

        if error == 0:
            processing_queue.put(Mol2Data(buff, enrg, name))

        processing_queue.put(posesfile)
    processing_queue.put(1)


compare_energy = lambda m1, m2: m1.total_energy > m2.total_energy
max_heap_size = 10000

heap = MinHeap(max_heap_size, comparator=compare_energy)
processing_queue = multiprocessing.Queue(maxsize=50)
posedata_producer_process = multiprocessing.Process(target=posedata_producer, args=(processing_queue, get_to_search(dockresults_path)))

posedata_producer_process.start()

hit_max = False

i = 0
while True:
    try:
        pose = processing_queue.get(True, 10)
    except:
        break

    # int signals start the clock
    if type(pose) == int:
        if pose == 0: # timer start
            i = 0
            start_time_u = time.clock_gettime(time.CLOCK_THREAD_CPUTIME_ID)
            start_time_r = time.time()
        if pose == 1: # end processing
            break
        continue

    # str signals to stop the clock, and also print the filename (which will be the item)
    elif type(pose) == str:
        end_time_u = time.clock_gettime(time.CLOCK_THREAD_CPUTIME_ID)
        end_time_r = time.time()
        elapsed_u  = end_time_u - start_time_u
        elapsed_r  = end_time_r - start_time_r
        print((i, "poses read from", pose))
        print(("time (user): {:15f}, time (real): {:15f}".format(elapsed_u, elapsed_r)))
        print(("pps  (user): {:15f}, pps  (real): {:15f}".format(i / elapsed_u, i / elapsed_r)))
        continue

    if heap.size == max_heap_size:
        if not hit_max:
            print("hit max poses for heap!")
            hit_max = True

        if compare_energy(pose, heap.minvalue()):
            del pose
            continue

        else:
            # pops the minimum value and inserts the new value in the same operation
            popped = heap.remove_insert(pose)
            del popped
    else:
        heap.insert(pose)

    i += 1

print("done processing!")

data_index = sorted([(i, heap.heap[i].total_energy) for i in range(heap.size)], key=lambda m:m[1])
with gzip.open(output_file, 'w') as outfile:

    for idx, out_energy in data_index:

        # gzip data can simply be concatenated together, so this works fine.
        outfile.write(heap.heap[idx].buf)




