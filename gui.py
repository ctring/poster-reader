from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
############################################
#  GUI cropper image using PIL and Tkinter #
############################################

# To use, go python pythonGUI.py 'filename'

from Tkinter import *
from PIL import ImageTk, Image
import sys
import os
import numpy
from word import recognize

BOX_LIMIT = 20
REC_OPTIONS = {'outline': 'red', 'width': 3}


master = Tk()
canvas = Canvas(master, width=600, height=600)

box = [0, 0, 0, 0]
boxes=[]

startx, starty = 0, 0
preview_rec = 0
drawn_items = []
restart = False

album=[]

with open('lexicon.txt') as lex_file:
 	lexicon = [line.rstrip('\n') for line in lex_file]

def mousePressed(event):
	global box, startx, starty, restart, drawn_items
	if restart:
		for item in drawn_items:
			canvas.delete(item)
		drawn_items = []
		restart = False

	box[0], box[1] = event.x, event.y
	startx,starty = event.x,event.y
	print("Mouse pressed: (%s %s)" % (event.x, event.y))


def mouseMoved(event):
	global box, boxes, preview_rec
	canvas.delete(preview_rec)
	preview_rec = canvas.create_rectangle(startx, starty, event.x, event.y,
																					  **REC_OPTIONS)


def mouseReleased(event):
	global box, boxes, preview_rec, drawn_items
	canvas.delete(preview_rec)
	box[2], box[3] = event.x, event.y
	if abs(box[2] - box[0]) > BOX_LIMIT and abs(box[3] - box[1]) > BOX_LIMIT:
		boxes.append(box)
		drawn = canvas.create_rectangle(*box, **REC_OPTIONS)
		drawn_items.append(drawn)
		box = [0,0,0,0]

		print("Mouse released: (%s %s)" % (event.x, event.y))


def keyDown(event):
	global album, drawn_items, canvas, boxes, restart
	if restart or len(boxes) == 0:
		return
	for b in boxes:
		try:
			cropImg = photo.crop(b)
			if cropImg.size[0] == 0 or cropImg.size[1] == 0:
				raise SystemError("Nothing to crop")

			val = numpy.asarray(cropImg.convert('L'))
			album.append(val)

		except SystemError as e:
			print("Error:" , e)

	print('Recognizing words...')
	result = recognize(album, lexicon, show_graph_first_one=False, verbose=False)
	for res in result:
		print('%s (%.4f)'%(res[0], res[1]))

	for i, b in enumerate(boxes):
		lower_x = min(b[0], b[2])
		lower_y = max(b[1], b[3])
		txt = canvas.create_text((lower_x + 5, lower_y),
																 text=result[i][0],
																 anchor='nw',
																 fill='white',
																 font=('arial', 25))
		bbox = canvas.bbox(txt)
		bbox_rec = canvas.create_rectangle(lower_x, lower_y, bbox[2] + 5, bbox[3] + 5,
																			 fill='red', **REC_OPTIONS)
		canvas.tag_raise(txt)
		drawn_items.append(txt)
		drawn_items.append(bbox_rec)

	restart = True
	boxes = []
	album = []


def binding(filename):
	global photo
	photo = Image.open(filename)
	img = ImageTk.PhotoImage(photo)

	canvas.config(width=photo.size[0],height=photo.size[1])
	canvas.create_image(0, 0, image=img, anchor='nw')
	canvas.bind('<Button-1>', mousePressed)
	canvas.bind('<Button1-Motion>', mouseMoved)
	canvas.bind('<ButtonRelease-1>', mouseReleased)
	master.bind('<Key>',keyDown)
	master.image = img
	canvas.pack()


if __name__=='__main__':
	if os.path.isfile(sys.argv[1]):
		binding(sys.argv[1])
		mainloop()
