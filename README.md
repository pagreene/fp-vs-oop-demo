# Functional Programming vs Object-Oriented Programming

This is a brief demo of the symmetry between functional programming (FP) and object oriented programming (OOP) approaches.

There are two solutions to the fairly simple problem
of taking a list of recipes with their ingredients listed out
and forming a shopping list. For the sake of simplicity,
it is assumed the pantry is empty, and anything needed for
the recipes must go on the list (no stock of supplies to
compare to).

## Functional Approach

You can see the functional approach in [functional.py](functional.py).
I utilized (perhaps even over-utilized for the sake of demonstration)
many of the functional tools that Python offers in its
core library, including `map`, `lamdba`, and `reduce`. You see
the use of first class functions, and just-in-time execution
using generators.

However, you may also find that it is fairly unclear what
is happening in many parts of the code. Because data
structures are immutable, extra thought is required
to do tasks such as accumulating value for a 
particular item.

## Object-Oriented Approach

This can be contrasted with the Object-Oriented approach in [oop.py](oop.py).
Here, the core calculation of the shopping list is
considerably simpler to interpret with mutability. It is
more natural to think of this as creating a list (or
dictionary) of items and updating their quantity as
you find more instances of that item.

However, it is also notable that there are far more
questions about state that become relevant in this approach.
For example, what if someone adds another recipe to the 
`ShoppingCart` instance? Should we rerun the `get_shopping_list()`
method every time just in case?

This complication is also an opportunity. In a functional context
there is no answer except "yes", you need to rerun the computation
every time. With the OOP approach, you could in principle
make it so changes to the list of recipes were detected,
and recalculation only happened as needed. But again: 
that creates its own kind of complexity.

Even though each part of the OOP implementation is a bit easier
and more intuitive to understand, its mutability
and the freedom of interactions between parts of
the code can make global behavior much harder to
predict.

## Which is better?

Ultimately, that is subjective, and I would argue it 
is also situational. However, I think for most case,
the answer is neither. I think trying to adhere purely
to one mode or the other is both futile and in most
cases leads to unwanted complexity.

It is notable that functional programs still require
classes, if only data classes, at some level. But even then,
there are at least usually a few primitive types that
have methods in a functional environment. And even if
they pretend otherwise with "static methods", OOP
needs simple functions.

I think that a good rule of thumb is that programs should
be functions at the surface, and that side-effects and 
mutability must be carefully considered and limited. However
it is valuable to have your data models define some 
select methods that are especially pertinent to
themselves. This keeps code close to the data it
manipulates.

In some cases, where extreme, provable reliability is
essential, or when the focus really is on the process applied
to the data, functional programming is probably the way to go.
On the other hand, when complex interactions between
stateful entities are the focus of your work, your code
will benefit from an object-oriented lens.
