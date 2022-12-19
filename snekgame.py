import pygame, time, random, threading, sys

save_filename = "../scores.txt"
def save_score():
    with open(save_filename, "a") as file:
        save_line = "{}:{}\n".format(score, username)
        file.write(save_line)
        file.close()

def IsBlockOutOfRange(block):
    return (block[0] >= window_x or block[1] >= window_y or block[0] < 0 or block[1] < 0)

def exit():
    counter_thread.stop()
    food_spawn_thread.stop()
    spike_spawn_thread.stop()
    pygame.quit()
    sys.exit(0)

def EventHandler(event: pygame.event.Event):
    global direction
    if event.type == pygame.QUIT:
        exit()
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
    counter_thread.stop()
    food_spawn_thread.stop()
    spike_spawn_thread.stop()

    save_score()
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
            exit()
            break

class CounterThread(threading.Thread):
    def setup(self):
        self.count = 0
        self.interval = 1
        self.enabled = False
        self.callbacks= []
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
            if not self.enabled:
                break
            self.count = self.count + 1
            if len(self.callbacks) > 0:
                for callback in self.callbacks:
                    callback(self.count)

    def on_increment(self, callback):
        self.callbacks.append(callback)
    def off_increment(self, callback):
        self.callbacks.remove(callback)
    def reset(self):
        self.count = 0
    def stop(self):
        self.enabled = False
        print("Stopped counter thread")
    def count(self):
        return self.count

class FoodSpawnThread(threading.Thread):
    def setup(self):
        self.blocks = None
        
        self.working = False
        self.interval = 10
    
    def run(self):
        if self.working:
            print("Food spawn already enabled")
            return
        self.working = True

        while self.working:
            time.sleep(self.interval)
            if not self.working:
                break
            x = round(random.randint(0, window_x-1), -1)
            y = round(random.randint(0, window_y-1), -1)
            if x >= window_x:
                x = x-10
            if y >= window_y:
                y = y-10
            block = (x,y)
            block_colour = display.get_at(block)
            if block_colour == bkg_colour:
                print("Spawning food at ", block)
                pygame.draw.rect(display, snek_food_colour, [block[0],block[1], snek_food_block_size, snek_food_block_size])
                pygame.display.update()
    def stop(self):
        self.working = False

class SpikeSpawnThread(threading.Thread):
    def setup(self):
        window_volume = (window_x) * (window_y) / (spike_block_size*spike_block_size)
        self.max_blocks = round(0.1 * window_volume)
        self.blocks = []
        self.num_of_blocks = 1
        self.working = False
        self.interval = 10

        print("Max spikes: ", self.max_blocks)
    def run(self):
        if self.working:
            print("Spike spawn already enabled")
            return
        self.working = True
        def SpawnNewBlocks():
            for block in self.blocks:
                pygame.draw.rect(display, bkg_colour, [block[0], block[1], spike_block_size, spike_block_size])
            self.blocks = []

            for n in range(self.num_of_blocks):
                x = round(random.randint(0, window_x-1), -1)
                y = round(random.randint(0, window_y-1), -1)
                if x >= window_x:
                    x = x-10
                if y >= window_y:
                    y = y-10
                block = (x,y)
                ok = False
                print(block)
                block_colour = display.get_at(block)
                if block_colour == bkg_colour:
                    adjacent_blocks: list[tuple] = [(block[0]-10,block[1]), (block[0]+10,block[1]), (block[0],block[1]-10),  (block[0],block[1]+10)]
                    for block_aj in adjacent_blocks:
                        if IsBlockOutOfRange(block_aj):
                            continue
                        colour = display.get_at(block_aj) 
                        if colour != bkg_colour:
                            if colour == spike_block_size:
                                ok = True
                            elif colour == snek_colour:
                                ok =False
                                break
                        else:
                            ok = True
                    if ok:
                        pygame.draw.rect(display, spike_colour, [block[0], block[1], spike_block_size, spike_block_size])
                        print("Spawned spike {} at {}".format(n, block))
                self.blocks.append(block)
                
        while self.working:
            time.sleep(self.interval)
            if not self.working:
                break
            SpawnNewBlocks()
            if self.num_of_blocks < self.max_blocks:
                self.num_of_blocks = self.num_of_blocks + 1
            pygame.display.update()

    def stop(self):
        self.working = False





def init():
    global blocks,direction, snek_length, score, loop_delay, counter_thread, food_spawn_thread, spike_spawn_thread
    
    score = 0
    snek_length = 1
    loop_count = 0
    blocks = [(200,200)]
    direction = [10,0]
    display.fill(bkg_colour)
    pygame.display.update()

    loop_delay = 0.3
    delay_step =  0.02
    loop_delay_min = 0.08

    def UpdateEachSecond(count):
        global score, window_x, window_y, display, loop_delay

        score = round(score + (snek_length))

        if count/10 == round(count/10): 
            if loop_delay > loop_delay_min:
                loop_delay = round(loop_delay - delay_step, 10)
                print("Increasing to "+ str(loop_delay))


    counter_thread = CounterThread()
    food_spawn_thread = FoodSpawnThread()
    spike_spawn_thread = SpikeSpawnThread() 

    spike_spawn_thread.setup()
    food_spawn_thread.setup()
    counter_thread.setup()

    counter_thread.start() 
    food_spawn_thread.start()
    spike_spawn_thread.start()
    
    counter_thread.on_increment(UpdateEachSecond)
    while True: 
        time.sleep(loop_delay)
        #if window_changed:
        #    for block in blocks:
        #        if block[0] < window_x or block[1] < window_y:
        #            pygame.draw.rect(display, snek_colour, [block[0],block[1],snek_block_size,snek_block_size])
                
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

        #print(new_snek_block)
        blocks.insert(0, new_snek_block)
        for event in pygame.event.get():
            EventHandler(event)

        block_color = display.get_at((x,y))
        if block_color == snek_food_colour:
            snek_length = snek_length + 1
        elif block_color == snek_colour or block_color == spike_colour:

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

score: int
username: str = input("Name: ")
#snek info
#(x,y)
blocks: list[tuple] 
direction: list[int]
snek_length = 1
snek_colour = (255,255,255)
snek_block_size = 10

snek_food_colour = (255, 0,0)
snek_food_block_size = 10

spike_colour = (191, 64, 191)
spike_block_size = 10
#display
window_x =  400
window_y =  400
pygame.init()
pygame.display.set_caption('Snek game (OblivCode)')
display=pygame.display.set_mode((window_x, window_y), pygame.RESIZABLE)
bkg_colour = (0,0,0)
clock = pygame.time.Clock()

#threads
counter_thread: CounterThread
food_spawn_thread: FoodSpawnThread
spike_spawn_thread: SpikeSpawnThread


init()
