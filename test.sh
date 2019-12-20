#!/bin/bash


mpirun -np 2 -H localhost:1,172.31.29.187:1 -bind-to none -map-by slot \
-x LD_LIBRARY_PATH  \
-x NCCL_SOCKET_NTHREADS=8 \
-x NCCL_DEBUG=INFO \
-x NCCL_SOCKET_IFNAME=^lo,docker,ens4 \
-mca btl_tcp_if_exclude lo,docker,ens4 \
./build/all_reduce_perf -b 16M -e 128M -f 2 -g 1 
