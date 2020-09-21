from amonguscapture.ProcessMemory import ProcessMemory
from amonguscapture.PlayerInfo import PlayerInfo
from enum import Enum
from time import sleep
import struct

class AmongUsGame():
    class GameState(Enum):
            LOBBY = 1
            TASKS = 2
            DISCUSSION = 3

    def __init__(self):
        self.ProcessMemory = ProcessMemory()
        self.hooked = self.ProcessMemory.HookProcess("Among Us")

        self.GameAssemblyPtr = 0
        self.UnityPlayerPtr = 0
        self.oldState = self.GameState.LOBBY
        if (self.hooked):
            modulesLeft = 2
            for module in self.ProcessMemory.modules:
                if modulesLeft == 0:
                    break
                elif module.Name.lower() == "GameAssembly.dll".lower():
                    self.GameAssemblyPtr = module.BaseAddress
                    modulesLeft -= 1
                elif module.Name.lower() == "UnityPlayer.dll".lower():
                    self.UnityPlayerPtr = module.BaseAddress
                    modulesLeft -= 1
            self.oldState = self.getState()

        self.playerColors = ["red", "blue", "green", "pink", "orange", "yellow", "black", "white", "purple", "brown", "cyan", "lime"]

    def inGame(self):
        return bool(self.ProcessMemory.ReadPointer(self.UnityPlayerPtr, [0x127B310, 0xF4, 0x18, 0xA8], 1)[0])

    def isHooked(self):
        return self.hooked

    def inMeeting(self):
        return bool(self.ProcessMemory.ReadPointer(self.UnityPlayerPtr, [0x12A7A14, 0x64, 0x54, 0x18], 1)[0])

    def getMeetingHudState(self):
        return self.ProcessMemory.ReadPointer(self.GameAssemblyPtr, [0xDA58D0, 0x5C, 0, 0x84], 1)[0]

    def getState(self):
        if not self.inGame():
            state = self.GameState.LOBBY
        elif self.inMeeting():
            state = self.GameState.DISCUSSION
        else:
            state = self.GameState.TASKS
        return state

    def getPlayers(self):
        allPlayersPtr = struct.unpack("<L", self.ProcessMemory.ReadPointer(self.GameAssemblyPtr, [0xDA5A60, 0x5C, 0, 0x24], 4))[0]
        if allPlayersPtr == 0:
            return None
        allPlayers = struct.unpack("<L", self.ProcessMemory.ReadPointer(allPlayersPtr, [0x8], 4))[0]
        playerCount = self.ProcessMemory.ReadPointer(allPlayersPtr, [0xC], 1)[0]
        playerAddrPtr = allPlayers + 0x10
        allPlayerInfos = []
        for i in range(playerCount):
            playerAddr = struct.unpack("<L", self.ProcessMemory.Read(playerAddrPtr, 4))[0]
            pi = PlayerInfo(struct.unpack("<xxxxxxxxBxxxLBxxxLLLBxxxLBBxxxL", self.ProcessMemory.Read(playerAddr, 49)))
            allPlayerInfos.append(pi)
            playerAddrPtr += 4
        return allPlayerInfos

    def getDeadPlayers(self, pinfo = None):
        dead = []
        if pinfo == None:
            players = self.getPlayers()
        else: 
            players = pinfo
        for p in players:
            if p.IsDead > 0:
                dead.append(p)
        return dead

    def getImposters(self, pinfo = None):
        imposters = []
        if pinfo == None:
            players = self.getPlayers()
        else: 
            players = pinfo
        for p in players:
            if p.IsImposter > 0:
                imposters.append(p)
        return imposters

    def main(self):
        while True:
            allPlayerInfos = self.getPlayers()
            if allPlayerInfos == None:
                continue
            state = self.getState()
            dead = [self.ProcessMemory.ReadString(p.PlayerName) for p in self.getDeadPlayers(allPlayerInfos)]
            imposters = [self.ProcessMemory.ReadString(p.PlayerName) for p in self.getImposters(allPlayerInfos)]
            print(f"State: {state}, Dead: {dead}, Imposters: {imposters}")
            self.oldState = state
            sleep(0.25)


if __name__ == '__main__':
    game = AmongUsGame()
    while not game.hooked:
        game = AmongUsGame()
    game.main()