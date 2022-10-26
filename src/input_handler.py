import pygame as pg

# Take care of user input and delegate bound functionality
class InputHandler:
    def __init__(self):
        self.pressed_keys = []
        self.recorded_text = ""
        self.recording = False
        self.recording_stop_key = pg.K_RETURN

    def handle(self, game):
        for event in pg.event.get():
            # On quit
            if event.type == pg.QUIT:
                game.quit()
                pg.quit()
                quit()

            # Key pressed
            if event.type == pg.KEYDOWN:
                if event.key not in self.pressed_keys:
                    self.pressed_keys.append(event.key)
                if self.recording: # If taking text input
                    if event.key == self.recording_stop_key:
                        self.stop_recording_text()
                    elif event.key == pg.K_BACKSPACE:
                        self.recorded_text = self.recorded_text[:-1]
                    else:
                        self.recorded_text += event.unicode
                else: # If not taking text input
                    # Cut
                    if not game.cutting and event.key == pg.K_q:
                        game.cut(game.fracplant)
                    # Save
                    if event.key == pg.K_s:
                        game.save()
                    if event.key == pg.K_r:
                        game.reset()
                    if event.key == pg.K_n:
                        game.set_name_prompt()
            
            # Key lifted
            if event.type == pg.KEYUP:
                if event.key in self.pressed_keys:
                    self.pressed_keys.remove(event.key)
    
    def start_recording_text(self, stop_key=pg.K_RETURN):
        self.recording = True
        self.recording_stop_key = stop_key

    def stop_recording_text(self):
        self.recording = False
        return self.recorded_text

    def get_recorded_text(self):
        return self.recorded_text

    def clear_recorded_text(self):
        self.recorded_text = ""

    # Check if a key is pressed
    def is_pressed(self, key):
        return key in self.pressed_keys

    # Remove a specific key from <pressed_keys>
    def pop_key(self, key):
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    # Clear <pressed_keys>
    def close(self):
        self.pressed_keys.clear()