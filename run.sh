#!/bin/bash


mpirun -np 2 -H localhost:1,172.31.29.187:1 -bind-to none -map-by slot \
-x LD_LIBRARY_PATH=/usr/local/nccl/lib:/usr/local/cuda/lib64  \
-x NCCL_SOCKET_NTHREADS=4 \
-x NCCL_DEBUG=INFO \
-x NCCL_SOCKET_IFNAME=^lo,docker,ens4 \
-mca btl_tcp_if_exclude lo,docker,ens4 \
./build/mdt_allreduce_perf -b 4M -e 4M -f 2 -g 1 -c 0
