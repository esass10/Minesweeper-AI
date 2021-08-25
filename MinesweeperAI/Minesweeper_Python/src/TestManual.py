from AI import AI
from Action import Action


class TestManual (AI):
 
    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
        self.__rowDimension = rowDimension
        self.__colDimension = colDimension

    def getAction(self, number: int) -> "Action Object":
        action = AI.Action(1)

        for i in range(0,2):
            return Action(action, 2, 3)
            return Action(action, 5, 1)
            return Action(action, 1, 1)
       
        return Action(action, 6, 6)
        
