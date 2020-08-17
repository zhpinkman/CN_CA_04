* terminal1:
> ryu-manager dijkstra_ryu.py --observe-links

* terminal2:
> sudo mn --topo tree,3 --controller remote


> sudo python2.7 test_mininet.py


* To fix occasional errors:
> sudo mn -c
