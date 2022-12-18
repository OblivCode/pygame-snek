import pygame, time, random, threading, sys





def EventHandler(event: pygame.event.Event):
    global direction
    if event.type == pygame.QUIT:
        pygame.quit()
    elif event.type == pygame.KEYDOWN:
        key = event.key
        if key == pygame.K_UP:
            print("UP")
            direction = [0, -snek_block_size]
        elif key == pygame.K_DOWN:
            print("DOWN")
            direction = [0, snek_block_size]
        elif key == pygame.K_LEFT:
            print("LEFT")
            direction = [-snek_block_size, 0]
        elif key == pygame.K_RIGHT:
            print("RIGHT")
            direction = [snek_block_size, 0]
            


def GameOver():
    display.fill(bkg_colour)

    font = pygame.font.SysFont(None, 30)
    text = font.render("Score "+str(score), True, (0,0,255))
    display.blit(text, (0,0))

    font = pygame.font.SysFont(None, 60)
    text = font.render("GAME OVER", True, (255,0,0))
    display.blit(text, (0,30))

    font = pygame.font.SysFont(None, 20)
    text = font.render("R to restart", True, (0,255,0))
    display.blit(text, (0,70))

    pygame.display.update()
    
    while True:
        event = pygame.event.wait()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                init()
                break
        elif event.type == pygame.QUIT:
            pygame.quit()

class CounterThread(threading.Thread):
    def setup(self):
        self.count = 0
        self.interval = 1
        self.enabled = False
        self.callback= None
        self.on_count_callback = None
        self.on_count_ = 0
        self.name = "Counter thread"
    def run(self):
        if self.enabled:
            print("Timer already working")
            return
        self.enabled = True
        while self.enabled:
            time.sleep(self.interval)
            self.count = self.count + 1
            if self.callback !=None:
                self.callback(self.count)
            if self.on_count_callback != None and self.count == self.on_count_:
                self.on_count_callback()
    def on_increment(self, callback):
        self.callback = callback
    def on_count(self, callback, count):
        self.on_count_callback = callback
        self.on_count_ = count
    def reset(self):
        self.count = 0
    def stop(self):
        self.enabled = False
    def count(self):
        return self.count

class FoodSpawnThread(threading.Thread):
    def setup(self):
        self.block = None
        self.working = False
        self.interval = 10
    
    def run(self):
        if self.working:
            print("Food spawn already enabled")
            return
        self.working = True
        while self.working:
            time.sleep(self.interval)
            x = round(random.randint(0, window_x), -1)
            y = round(random.randint(0, window_y), -1)
            block = (x,y)
            block_colour = display.get_at(block)
            if block_colour == bkg_colour:
                print("Spawning food at ", block)
                pygame.draw.rect(display, snek_food_colour, [block[0],block[1], snek_food_block_size, snek_food_block_size])
                pygame.display.update()
    def stop(self):
        self.working = False




def init():
    global blocks
    global direction
    global snek_length
    global food_spawn_thread_flag
    global second_counter_thread_flag
    global score

    score = 0

    food_spawn_thread_flag = 0
    second_counter_thread_flag = 0
    snek_length = 1
    loop_count = 0
    blocks = [(200,200)]
    direction = [10,0]
    display.fill(bkg_colour)
    pygame.display.update()

    def UpdateScore(count):
        global score
        score = score + snek_length

    food_spawn_thread = FoodSpawnThread()
    food_spawn_thread.setup()
    counter_thread = CounterThread()
    counter_thread.setup()
    food_spawn_thread.start()
    counter_thread.start()
    counter_thread.on_increment(UpdateScore)
    while True:
        
        time.sleep(loop_delay)
        if not food_spawn_thread.is_alive:
            food_spawn_thread.start()
        #snek_pos = blocks[0]
        x = blocks[0][0]+direction[0]
        y = blocks[0][1]+direction[1]
    

        if x > window_x-1 or x < 0 or y > window_y-1 or y < 0:
            GameOver()
            break
        #new_snek_block = (snek_pos[0]+direction[0], snek_pos[1]+direction[1])
        new_snek_block = (x,y)

        print(new_snek_block)
        blocks.insert(0, new_snek_block)
        for event in pygame.event.get():
            EventHandler(event)

        block_color = display.get_at((x,y))
        if block_color == snek_food_colour:
            snek_length = snek_length + 1
        elif block_color == snek_colour:
            GameOver()
            break

        pygame.draw.rect(display, snek_colour, [x,y,snek_block_size,snek_block_size])

        if len(blocks) > snek_length: 
            last_idx = len(blocks)-1
            old_snek_block = blocks[last_idx]
            blocks.remove(old_snek_block)
            pygame.draw.rect(display, bkg_colour, [old_snek_block[0], old_snek_block[1], snek_block_size,snek_block_size])
        
        pygame.display.update()
        loop_count = loop_count + 1

#snek info
score: int
#(x,y)
blocks: list[tuple] 
direction: list[int]
snek_length = 1
snek_colour = (255,255,255)
snek_block_size = 10

snek_food_colour = (255, 0,0)
snek_food_block_size = 10
snek_food_spawn_count = 50
#display
window_x =  400
window_y =  400
pygame.init()
pygame.display.set_caption('Snek game (OblivCode)')
display=pygame.display.set_mode((window_x, window_y))
bkg_colour = (0,0,0)
clock = pygame.time.Clock()

loop_delay = 0.5

init()
