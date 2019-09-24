import cv2
import filetrans
import datetime


def take_photo():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    now_time = datetime.datetime.now()
    print(str(now_time))
    name = str(now_time)
    new_name = name.replace(" ", "_")
    print(new_name)
    cv2.imwrite(new_name + '.jpg', frame)
    print("1")
    cv2.imshow("capture", frame)
    print("2")
    file_name = new_name + '.jpg'
    filetrans.run(file_name)                       # 发送图片到控制端
    cap.release()
    cv2.destroyAllWindows()


