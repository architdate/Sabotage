Roles:
@everyone: no speak permissions in among us channels
Crewmate: "/" perm for speak permissions in among us vc

Prereq
- all users need to have a diff name
- dont start the bot midgame

StartGame: (command)
- cog init variable if game has started
- store game object as cog variable
- start the loop function

StopGame: (command)
- set StartGame to false
- stop the loop
- clear the game object from cog variable

Register:
- allow multiple registrations
- storage: {<discordid>: <playername>}
- on multiple registration, just update the dict with new playername
- if registrations.values() already has the playername someone is trying to register, then tell them to fuck off
- on register give crewmate role

Unregister:
- yeet them out the dict

Loop func:
- check every 0.25 secs
- check state
- if state is same as old state: do nothing
- if state is changed and state is discussion: server unmute people who arnt dead
- if state is changed and state is task: server mute everyone registered in vc
- if state is changed and state is lobby: server unmute everyone registered in vc

on voice join event handler:
- if startgame is false: server unmute if registered
- if startgame is true and person is server muted and person is not dead and game state is not tasks: server unmute
- if startgame is true and person is not server muted: if person is dead: server mute or if game state is tasks: server mute