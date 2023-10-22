# Using this file to track tricky decision points, the chosen solution(s), and why

- (0.0.1) When working with local objects there is no internal unique_id on initial object creation. I was thinking this might be a problem in the context of bulk inserts to not have unique_id's locally and the simplest fix was to just make them locally. The biggest pain point here is needing to manage the multiple types of upstream unique_id's available in various graph providers.

Initially the str and uuid types are **generally** compatible code wise, str types that require an index are slightly more difficult e.g PRE_000001. Integers shouldn't be too complex the only difficulty there is managing the differences in code between the str data types. There is however another worrying scenario.

In highly concurrent scenario's this changes and only the uuid type is immune to unique_id contention, in the others it might be necessary to batch some number of "reserved" id's before then creating the items in the graph. If 10 processes are all attempting to bulk insert on anything that isn't the uuid type. There probably needs to be some mechanism that can be handed to the programmer that lets them marshall these id's in a way that they can then plug into the OGM class.

I'll need to think about the best way to implement this "UniqueIdProvider" that adds support for these other types of unique_ids'. The graph providers I'm familiar with allow for mixing uuid and str unique_id so thinking from that perspective first is probably the easiest to start with. For a getting things working perspective I think focusing on the uuid unique_id type and creating id's locally during object creation both simplifies the code and the implementation details of some of these base classes.

I need to spend some time thinking about how to implement the concept of a "UniqueIdProvider", what the API for that would look like, and if its possible to provide a default UUID implementation. My major concern with the other types is the unique_id batching and the potential for high complexity and ephemeral failures along with how to test it. With these conflicting id's using the `Merge.onCreate` strategy may work in some cases, but in others may not be desirable.

All of the above might be somewhat minimized with use of transactions, but will still need a way to do the unique_id bulking as far as I can tell.

- (0.0.1) TODO
- (0.0.1) TODO
- (0.0.1) TODO
- (0.0.1) TODO
- (0.0.1) TODO
- (0.0.1) TODO
