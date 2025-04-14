#!/usr/bin/env python

#adapted from http://www.inside-r.org/packages/cran/enrichvs/docs/bedroc
#BEDROC implementation of Truchon & Bayly 
#http://www.ncbi.nlm.nih.gov/pubmed/17288412
"""
bedroc <- function(x, y, decreasing=TRUE, alpha=20.0) {
  if ( length(x) != length(y) ){
    stop(paste("The number of scores must be equal to the number of labels."))
  }
  N <- length(y)
  n <- length( which(y==1) )
  ord <- order(x, decreasing=decreasing)
  m_rank <- which( y[ord] == 1 )
  s <- sum( exp(-alpha * m_rank / N ) )
  ra <- n / N
  ri <- (N - n) / N
  random_sum <- ra * exp( -alpha / N )*(1.0 - exp( -alpha ) )/ ( 1.0 - exp( -alpha / N ) )
  fac <- ra * sinh( alpha / 2.0 ) / ( cosh(alpha / 2.0 ) - cosh(alpha / 2.0 - alpha * ra ) )
  cte = 1.0/ ( 1 - exp( alpha * ri) )
  return( s / random_sum * fac + cte )

}
"""
