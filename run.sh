#!/bin/bash


mpirun -np 2 -H localhost:1,172.31.29.187:1 -bind-to none -map-by slot \
-x LD_LIBRARY_PATH=/usr/local/nccl/lib:/usr/local/cuda/lib64  \
-x NCCL_SOCKET_NTHREADS=4 \
-x NCCL_DEBUG=INFO \
-x NCCL_SOCKET_IFNAME=^lo,docker,ens4 \
-mca btl_tcp_if_exclude lo,docker,ens4 \
./build/mdt_allreduce_perf -b 100M -e 100M -f 2 -g 1 -c 0 -w 0 -l /home/ubuntu/chaokun_logs/20191220-034144-40Gbit-100Gbit-4p3dn-ResNet50-imagenet/log_for_dt_mimic.txt
