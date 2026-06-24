# MathQuest

## Where is the options page?

The [player options page for this game](../player-options) contains all the options you need to configure and export a
config file.

## What is MathQuest?

MathQuest is an original game made entirely by NewSoupVi.
It is a minimal 8bit-era inspired adventure game with grid-like movement.
It is about 20 seconds long. However, the client can seamlessly switch between different slots,
so if you want to have 10 of them, that should work pretty well.

Crucially, this game is entirely integrated into the client sitting inside its .apworld.
If you have the .apworld installed into your [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases/latest)
install, you can play MathQuest.

## Why does MathQuest exist?

MathQuest is implemented to be an example .apworld that can be used as a learning tool for new .apworld developers.
Its [source code](https://github.com/NewSoupVi/Archipelago/tree/MathQuest/worlds/MathQuest)
contains countless comments explaining how each part of the World API works.
Also, as of the writing of this setup guide (2025-08-24), it is up to date with all the modern Archipelago APIs.

The secondary goal of MathQuest is to be a semi-minimal generic world that is owned by Archipelago.
This means it can be used for Archipelago's unit tests without fear of eventual removal.

Finally, MathQuest was designed to be the first ever "game inside an .apworld",
where the entire game is coded in Python and Kivy and is playable from within its CommonClient-based Client.
I'm not actually sure if it's the first, but I'm not aware of any others.

## Once I'm inside the MathQuest client, how do I actually play MathQuest?

WASD or Arrow Keys for movement.
Space to swing your sword (if you have it) or interact with objects.
C to fire the Confetti Cannon.

Open chests, slash bushes, open doors, press buttons, defeat enemies.
Once you beat the dragon in the top right room, you win.
That's all there is! Have fun!

## A statement on the ownership over MathQuest

MathQuest is licensed using the [MIT license](https://opensource.org/license/mit),
meaning it can be modified and redistributed by anyone for any purpose.
However, Archipelago has its own ownership structures built ontop of the license.
These ownership structures call into question whether any world implementation can permanently be relied on.

In terms of these non-binding, non-legal Archipelago ownership structures, I will make the following statement.

I, NewSoupVi, hereby relinquish any and all rights to remove MathQuest from Archipelago.
This applies to all parts of MathQuest with the sole exception of the music and sounds.
If I want the sounds to be removed, I must do so via a PR to the Archipelago repository myself.
Said PR must keep MathQuest intact and playable, just with the music removed.

As long as I am the maintainer of MathQuest, I wish to act as such.
This means that any updates to MathQuest must go through me.

However, if I ever cease to be the maintainer of MathQuest,
due to my own wishes or because I fail to uphold the maintainership "contract",
the maintainership of MathQuest will go to the Core Maintainers of Archipelago, who may then decide what to do with it.
They can decide freely, but if the maintainership goes to another singular person,
it is my wish that this person adheres to a similar set of rules that I've laid out here for myself.

Hopefully, this set of commitments should ensure that MathQuest will forever be an apworld that can be relied on in Core.
If the ownership structures of Archipelago change,
I trust the Core Maintainers (or the owners in general) of Archipelago to make reasonable assumptions
about how this statement should be reinterpreted to fit the new rules.
