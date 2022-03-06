import pyautogui
import canvas

def get_targets():
    list_of_targets = []
    objects = pyautogui.locateAllOnScreen("LittleRat1.png", region=(415, 300, 1090, 480), grayscale=True, confidence=0.7)
    if objects:
        for cords in objects:
            list_of_targets.append((cords.left, cords.top))
    else:
        print("unable to locate objects")
    print(f"found {list_of_targets}")
    return list_of_targets

# Box(left=550, top=504, width=52, height=14)

if __name__ == "__main__":
    print(get_targets())
    canvas = canvas.Overlay()
    canvas.draw(get_targets())