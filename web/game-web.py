import game

class WebGame(game.Game):
    def start(self):
        # 블럭 줄 없애기
        self.b.clear()

        # 블럭을 초기화 하고 게임 오버 여부를 판단
        if self.make_block() == False:
            # game over
            self.b.b[self.b.b > 0] = 8
            # display
            return
   