import os
import time
import sys
import struct
import pyfits
import numpy as np
import scipy.misc as spy
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


class TestVector(object):
    def __init__(self):
        self.payload = ''

    @staticmethod
    def gen_rearrange(data):
        rawdata = bytearray(data)
        # for i in range(0, len(rawdata), 4):
        #        temp = rawdata[i:i+4]
        #        rawdata[i+0] = temp[1]
        #        rawdata[i+1] = temp[0]
        #        rawdata[i+2] = temp[3]
        #        rawdata[i+3] = temp[2]

        return memoryview(rawdata).tobytes()

    def image(self, filename, shift=0, imsize=[512, 512]):
        image = mpimg.imread(filename)
        image = spy.imresize(image, imsize)[:, :, 0]

        # image = image[:,:,0].reshape([1, 512*512])
        # shift values and convert to 32 bit integer
        image = image * np.power(2, shift)
        image = np.floor(image)
        image = np.int32(image)
        # image = image.transpose()

        # fimage = np.fft.fft2(image)
        # img3 = np.empty([512, 512], np.complex)
        # for i in range(512):
        #        img3[::,i] = np.fft.fft(image[::,i])#

        # img4 = np.empty([512, 512], np.complex)
        # for i in range(512):
        #        img4[i,::] = np.fft.fft(img3[i,::])

        # img5 = np.fft.ifft2(fimage)

        # f = np.fft.fft(image)
        # fimg = np.empty([512, 512])
        # fimg[::, ::] = abs(f)#.transpose()

        y = image.reshape([1, imsize[0] * imsize[1]])
        # y = fimage.reshape([1, 512*512])

        # plt.subplot(1,2,1)
        plt.imshow(image)
        # plt.subplot(1,2,2)
        # plt.imshow(abs(img5))
        plt.show()

        # build complex vales with imaginary part zero
        c = np.empty((2 * y.size,), dtype=y.dtype)
        c[0::2] = y.real
        c[1::2] = y.imag

        self.payload = self.gen_rearrange(c)
        return self.payload

    def black(self, imsize=[512, 512]):

        # build complex vales with imaginary part zero
        c = np.empty((2 * imsize[0] * imsize[1],), dtype=np.uint32)
        c[0::2] = 0
        c[1::2] = 0

        self.payload = self.gen_rearrange(c)
        return self.payload

    def white(self, imsize=[512, 512]):

        # build complex vales with imaginary part zero
        c = np.empty((2 * imsize[0] * imsize[1],), dtype=np.uint32)
        c[0::2] = 0xffffffff
        c[1::2] = 0xffffffff

        self.payload = self.gen_rearrange(c)
        return self.payload

    def pattern(self, imsize=[512, 512]):

        # build complex vales with imaginary part zero
        c = np.empty((2 * imsize[0] * imsize[1],), dtype=np.uint32)
        c[0::4] = 0xffffffff
        c[1::4] = 0xffffffff

        c[2::4] = 0x0
        c[3::4] = 0x0

        self.payload = self.gen_rearrange(c)
        return self.payload

    def fits(self, filename, shift=0, imsize=[512, 512]):
        hdu_list = pyfits.open(filename)
        image = hdu_list[0].data
        image = spy.imresize(image, imsize)[:, :]
        [x, y] = image.shape

        image = np.floor(image)
        image = np.int32(image)

        plt.imshow(image, cmap='gray')
        plt.show()

        image = image.reshape([1, x * y])
        c = np.empty((2 * image.size,), dtype=image.dtype)
        c[0::2] = image.real
        c[1::2] = image.imag

        self.payload = self.gen_rearrange(c)
        return self.payload

    @staticmethod
    def ret_image(data, shift=0):
        data = TestVector.gen_rearrange(data)
        c = np.frombuffer(data, np.uint32)
        y = np.empty(512 * 512, np.complex)
        y.real = c[0::2]
        y.imag = c[1::2]

        y = y.reshape([512, 512])
        by = y / np.power(2, shift)
        # print(by.min())
        # print(by.max())
        plt.subplot(2, 1, 1)
        plt.imshow(by.real)
        plt.subplot(2, 1, 2)
        plt.plot(by[0, ::].real)
        plt.show()
        # by = by.astype(np.complex)
        # by = 255 * by / by.max()
        # mpimg.imsave('image_real.png', by.real, cmap='gray')
        # mpimg.imsave('image_image.png', by.imag, cmap='gray')

    def gen_sindata(self, length, freq, shift=0):
        # generate sine test vector
        t = np.linspace(0, 2 * np.pi, length)
        y = np.zeros(len(t))
        for i in range(len(freq)):
            y += 1.0 + np.sin(freq[i] * t)

        plt.plot(y)
        plt.show()
        # print(y)

        # shift values and convert to 32 bit integer
        y = y * np.power(2, shift)
        y = np.floor(y)
        y = np.int32(y)

        # build complex vales with imaginary part zero
        c = np.empty((2 * y.size,), dtype=y.dtype)
        c[0::2] = 0
        c[1::2] = y

        self.payload = self.gen_rearrange(c)

    def gen_sindata2(self, length, freq, shift=0):
        # generate sine test vector
        t = np.linspace(0, 2 * np.pi, length)
        y = np.zeros(len(t))
        for i in range(len(freq)):
            y += np.sin(freq[i] * t)

        img = np.empty([length, length])
        img[::, ::] = y

        img = img.transpose()

        print(img.min())
        print(img.max())

        # shift values and convert to 32 bit integer
        y = img * np.power(2, shift)
        y = np.floor(y)
        y = np.int32(y)

        f = np.fft.fft(y)
        fimg = np.empty([length, length])
        fimg[::, ::] = abs(f)
        # fimg = fimg.transpose()

        plt.subplot(1, 2, 1)
        plt.imshow(img)
        plt.subplot(1, 2, 2)
        # plt.imshow(fimg)
        plt.plot(abs(fimg[::, 0]))
        plt.show()

        y = y.reshape(512 * 512)

        # build complex vales with imaginary part zero
        c = np.empty((2 * y.size,), dtype=y.dtype)
        c[0::2] = y
        c[1::2] = 0

        self.payload = self.gen_rearrange(c)

    def ret_image32(self, data):
        rawdata = bytearray(data)
        for i in range(0, len(rawdata), 4):
            temp = rawdata[i:i + 4]
            rawdata[i + 0] = temp[3]
            rawdata[i + 1] = temp[2]
            rawdata[i + 2] = temp[1]
            rawdata[i + 3] = temp[0]
        c = np.frombuffer(rawdata, np.uint32)
        # d = np.empty([2048* 2048])
        # print(len(d))
        c = c.astype(np.float32)
        d = c.reshape([2048, 2048])
        print(d[0, 0:4])
        # d = d / d.max()

        plt.imshow(d)
        plt.show()

    def gen_chlink_pattern(self):
        y = np.linspace(0, 2047, 2048)
        z = np.empty([2048, 2048])
        z[::, ::] = y

        self.gen_chlink_data(z)

    def gen_chlink_data(self, pattern):
        data = np.floor(pattern)
        data = (np.uint16(data) & 0xfff) << 2
        payload = bytearray(data)

        f = open('chlink_pattern.raw', 'wb')
        f.write(payload)
        f.close()

    def import_chlink_pattern(self):
        f = open('chlink_rcv_pattern.raw', 'rb')
        data = f.read()
        f.close()
