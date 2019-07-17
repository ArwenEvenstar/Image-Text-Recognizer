import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import skimage
from skimage import segmentation
import matplotlib.patches as patches

image = np.invert(np.asarray(Image.open("passage_cambria.PNG"))[:,:,0]) #greyscale
copy = np.copy(image)

#line segmentation
blurred = skimage.filters.gaussian(skimage.morphology.dilation(skimage.morphology.dilation(copy)), sigma=.6)
binary = blurred > skimage.filters.threshold_otsu(blurred)

label_image = skimage.measure.label(segmentation.clear_border(binary), connectivity=2)
image_label_overlay = skimage.color.label2rgb(label_image, image=image)
rects = []
for region in skimage.measure.regionprops(label_image):
    minr, minc, maxr, maxc = region.bbox
    rect = patches.Rectangle((minc, minr), maxc - minc, maxr - minr,fill=False, edgecolor='red', linewidth=2)
    rects.append(rect)
rect_dict = {}
for i in rects:
    rect_dict[i] = [i.xy[1]]
rect_sorted_dict = sorted(rect_dict, key = lambda k: (rect_dict[k]))
lines = []
y_coord = []
for i in range(len(rect_sorted_dict)):
    y1 = rect_sorted_dict[i].xy[1]  
    y2 = y1 + rect_sorted_dict[i].get_height()
    flag = 0
    for j in range(len(y_coord)):
        if y1<y_coord[j][1]:
            if y2>y_coord[j][1]:
                y_coord[j][1] = y2+1
                flag = 1
            else:
                flag = 1
    if flag == 0:
        y_coord.append([y1-10,y2])
for i in range(len(y_coord)):
    lines.append(copy[y_coord[i][0]:y_coord[i][1]+5,:])

#word segmentation    
words = []
for k in range(len(lines)):
    tmp_word = []
    img_word = lines[k]
    blurred_word = skimage.filters.gaussian(skimage.morphology.dilation(skimage.morphology.dilation(img_word)), sigma=.6)
    binary_word = blurred_word > skimage.filters.threshold_otsu(blurred_word)
    label_image_word = skimage.measure.label(segmentation.clear_border(binary_word), connectivity=2)
    image_label_overlay_word = skimage.color.label2rgb(label_image_word, image=img_word)
    rects_word = []
    for region in skimage.measure.regionprops(label_image_word):
        minr, minc, maxr, maxc = region.bbox
        rect = patches.Rectangle((minc, minr), maxc - minc, maxr - minr,fill=False, edgecolor='red', linewidth=2)
        rects_word.append(rect)
    rect_dict_word = {}
    for i in rects_word:
        rect_dict_word[i] = [i.xy[0]]
    rect_sorted_dict_word = sorted(rect_dict_word, key = lambda k: (rect_dict_word[k]))
    for i in range(len(rect_sorted_dict_word)):
        x1 = rect_sorted_dict_word[i].xy[0]
        y1 = rect_sorted_dict_word[i].xy[1]  
        x2 = x1 + rect_sorted_dict_word[i].get_width()
        y2 = y1 + rect_sorted_dict_word[i].get_height()
        tmp_word.append(img_word[y1:y2, x1:x2])
    words.append(tmp_word)
word_count = 0
for i in range(len(words)):
    for j in range(len(words[i])):
        word_count += 1
char_rects = []
for i in range(len(words)):
    s_word_mini_rects = []
    for j in range(len(words[i])):
        mini_image = words[i][j]
        mini_blurred = skimage.filters.gaussian(mini_image, sigma=0.6)
        mini_binary = mini_blurred > skimage.filters.threshold_otsu(mini_blurred)
        mini_cleared = segmentation.clear_border(mini_binary)
        mini_label_image = skimage.measure.label(mini_cleared, connectivity=2)
        mini_image_label_overlay = skimage.color.label2rgb(mini_label_image, image=mini_image)
        mini_rects = []
        for region in skimage.measure.regionprops(mini_label_image):
            minr, minc, maxr, maxc = region.bbox
            rect = patches.Rectangle((minc, minr), maxc - minc, maxr - minr,
                                          fill=False, edgecolor='red', linewidth=2)
            if maxc-minc > 3 and maxr-minr>3:
                mini_rects.append(rect)
        smini_rects = sorted(mini_rects, key = lambda obj: obj.xy[0])
        s_word_mini_rects.append(smini_rects)
    char_rects.append(s_word_mini_rects)

#character segmentation
characters = []
for i in range(len(char_rects)):
    character_word = []
    for j in range(len(char_rects[i])):
        character_line = []
        for k in range(len(char_rects[i][j])):
            x1 = char_rects[i][j][k].xy[0]
            y1 = char_rects[i][j][k].xy[1]
            x2 = x1 + char_rects[i][j][k].get_width()
            y2 = y1 + char_rects[i][j][k].get_height()
            character_line.append(words[i][j][:,x1:x2])
        character_word.append(character_line)
    characters.append(character_word)
for i in range(len(characters)):
    for j in range(len(characters[i])):
        for k in range(len(characters[i][j])):
            for l in range(len(characters[i][j][k])):
                for m in range(len(characters[i][j][k][l])):
                    if characters[i][j][k][l][m] != 0:
                        characters[i][j][k][l][m] = 255
                        
#resize according to requirements    
resize_img = []
for i in range(len(characters)):
    for j in range(len(characters[i])):
        for k in range(len(characters[i][j])):
            shrunk = np.asarray(Image.fromarray(characters[i][j][k]).resize((80,100),Image.ANTIALIAS))
            resize_img.append(scaler.transform(np.pad(shrunk,((14,14),(24,24)),'constant',constant_values=(0))))

