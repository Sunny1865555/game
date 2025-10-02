import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

FINGERTIP_IDS = [4, 8, 12, 16, 20]
FINGER_PIP_IDS = [None, 6, 10, 14, 18]


def count_fingers(hand_landmarks, handedness_label, image_width, image_height):
	pts = [(int(lm.x * image_width), int(lm.y * image_height)) for lm in hand_landmarks.landmark]

	fingers_up = 0

	# Thumb
	tip_x = pts[4][0]
	mcp_x = pts[2][0]
	if handedness_label == "Right":
		if tip_x > mcp_x:
			fingers_up += 1
	else:
		if tip_x < mcp_x:
			fingers_up += 1

	# Index, Middle, Ring, Pinky
	for tip_id, pip_id in zip(FINGERTIP_IDS[1:], FINGER_PIP_IDS[1:]):
		tip_y = pts[tip_id][1]
		pip_y = pts[pip_id][1]
		if tip_y < pip_y:
			fingers_up += 1

	return fingers_up


def main():
	cap = cv2.VideoCapture(0)
	if not cap.isOpened():
		print("Could not open webcam.")
		return

	with mp_hands.Hands(
		static_image_mode=False,
		max_num_hands=2,
		min_detection_confidence=0.6,
		min_tracking_confidence=0.6,
		model_complexity=1,
	) as hands:

		while True:
			ok, frame = cap.read()
			if not ok:
				break

			# Mirror view
			frame = cv2.flip(frame, 1)
			h, w = frame.shape[:2]

			# MediaPipe expects RGB
			rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			rgb.flags.writeable = False
			results = hands.process(rgb)
			rgb.flags.writeable = True

			if results.multi_hand_landmarks and results.multi_handedness:
				for hand_lms, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
					label = handedness.classification[0].label  # "Left" or "Right"
					cnt = count_fingers(hand_lms, label, w, h)

					mp_drawing.draw_landmarks(
						frame,
						hand_lms,
						mp_hands.HAND_CONNECTIONS,
						mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
						mp_drawing.DrawingSpec(color=(0, 150, 255), thickness=2),
					)

					wrist = hand_lms.landmark[0]
					x, y = int(wrist.x * w), int(wrist.y * h)
					cv2.putText(
						frame,
						f"{label} hand: {cnt}",
						(x - 40, y - 20),
						cv2.FONT_HERSHEY_SIMPLEX,
						0.8,
						(0, 0, 255),
						2,
						cv2.LINE_AA,
					)

				# If two hands present, show total
				total = sum(
					count_fingers(hl, hd.classification[0].label, w, h)
					for hl, hd in zip(results.multi_hand_landmarks, results.multi_handedness)
				)
				cv2.putText(
					frame,
					f"Total fingers: {total}",
					(10, 30),
					cv2.FONT_HERSHEY_SIMPLEX,
					1.0,
					(255, 255, 0),
					2,
					cv2.LINE_AA,
				)

			cv2.imshow("Finger Counter (q to quit)", frame)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break

	cap.release()
	cv2.destroyAllWindows()


if __name__ == "__main__":
	main()


