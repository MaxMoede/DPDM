# WUMPUS WORLDS

A great way to get a new world created is to the run the following command, 
and copy-paste the printed world, where size is changed to be the new size desired:

``` 
$ python3 Wumpsim.py -manual -size 6 
```

In the file below, I made recommendations on the maximum number of moves needed to solve
the puzzle. These are typically on the _very_ generous side, taking into account additional
movements for the agent to explore the cave.


### ASCII World Template
This world simply can be used as a template for other worlds.

### Basic Testworld
This is a very basic testing world. Nothing complicated or challenging.


## Worlds Designed for Students
The following worlds are designed to challenge and test students, starting off easy
and becoming more and more difficult.

### World 1
This is the same as the `Basic Testworld` above. Nothing complicated or challenging.

```  
$ python3 WumpusWorldParser.py worlds/world1.txt worlds/world1.out
$ python3 Wumpsim.py -world="worlds/world1.out" -max-moves=160
```

### World 2
Slightly larger world, designed to complicate things a bit, but still has static wumpus.

```  
$ python3 WumpusWorldParser.py worlds/world2.txt worlds/world2.out
$ python3 Wumpsim.py -world="worlds/world2.out" -max-moves=360
```

### World 3
Back to the smaller world, but now there are walls for difficulty. Still has static wumpus.

```  
$ python3 WumpusWorldParser.py worlds/world3.txt worlds/world3.out
$ python3 Wumpsim.py -world="worlds/world3.out" -max-moves=160
```

### World 4
Mid-sized world with 4 symmetric wumpus/gold locations and the first rotating wumpus.

```  
$ python3 WumpusWorldParser.py worlds/world4.txt worlds/world4.out
$ python3 Wumpsim.py -world="worlds/world4.out" -max-moves=360
```

### World 5
Complex world that is large with multiple pit, wumpus, and gold locations and varying
wumpus rotations and static locations with walls forming a maze.

```  
$ python3 WumpusWorldParser.py worlds/world5.txt worlds/world5.out
$ python3 Wumpsim.py -world="worlds/world5.out" -max-moves=1440
```

### World 6
Mid-sized world that requires correct processing of pit locations. The world has one
movable wumpus and one gold location with walls.

```  
$ python3 WumpusWorldParser.py worlds/world6.txt worlds/world6.out
$ python3 Wumpsim.py -world="worlds/world6.out" -max-moves=360
```

### World 7
Mid-sized maze world with no pits and a static wumpus in an interesting location.

```  
$ python3 WumpusWorldParser.py worlds/world7.txt worlds/world7.out
$ python3 Wumpsim.py -world="worlds/world7.out" -max-moves=500
```

### World 8
Small world with no pits and a static wumpus in a location not adjacent to the gold location.

```  
$ python3 WumpusWorldParser.py worlds/world8.txt worlds/world8.out
$ python3 Wumpsim.py -world="worlds/world8.out" -max-moves=160
```