"""refactored from https://github.com/tensorflow/tpu/issues/455

based on the error:
    InvalidArgumentError:  jpeg::Uncompress failed. Invalid JPEG data or crop window.
	 [[{{node decode_image/DecodeImage}}]]
	 [[IteratorGetNext]] [Op:__inference_test_function_56966]
"""

import os
from struct import unpack

from tqdm import tqdm

marker_mapping = {
    0xffd8: "Start of Image",
    0xffe0: "Application Default Header",
    0xffdb: "Quantization Table",
    0xffc0: "Start of Frame",
    0xffc4: "Define Huffman Table",
    0xffda: "Start of Scan",
    0xffd9: "End of Image"
}


class JPEG:
    """check which file cannot be decoded"""
    def __init__(self, image_file):
        with open(image_file, 'rb') as f:
            self.img_data = f.read()
    
    def decode(self):
        data = self.img_data
        while(True):
            marker, = unpack(">H", data[0:2])
            if marker == 0xffd8:
                data = data[2:]
            elif marker == 0xffd9:
                return
            elif marker == 0xffda:
                data = data[-2:]
            else:
                lenchunk, = unpack(">H", data[2:4])
                data = data[2+lenchunk:]            
            if len(data)==0:
                raise TypeError("issue reading jpeg file")          


def get_corrupted_files(dir, delete=False):
    """get list of corrupted files and delete them"""

    corrupt_list = []
    for path in tqdm(os.listdir(dir)):
        if path.endswith(".jpg"):
            imgpath = os.path.join(dir, path)
            image = JPEG(imgpath) 
            try:
                image.decode()
            except:
                corrupt_list.append(imgpath)
    
    if len(corrupt_list)==0:
        print("no corrupted files found")
    else:
        print(corrupt_list)
    
    if delete:
        for i in corrupt_list:
            os.remove(i)

            
if __name__ == "__main__":
    dir = "img/flowernot"
    get_corrupted_files(dir, delete=True)