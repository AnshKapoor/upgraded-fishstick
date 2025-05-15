import os
import time
import sys
import struct
import pyfits
import numpy as np
import scipy.misc as spy
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

class Image():

        def __init__(self, cmplx_out=False, image=None):
                self.image_re = image
                self.image_im = image
                self.cmplx_out = cmplx_out
                self.shift = 0

        @staticmethod
        def gen_rearrange(data):
                rawdata = bytearray(data)
                #for i in range(0, len(rawdata), 4):
                #        temp = rawdata[i:i+4]
                #        rawdata[i+0] = temp[1]
                #        rawdata[i+1] = temp[0]
                #        rawdata[i+2] = temp[3]
                #        rawdata[i+3] = temp[2]
                
                return memoryview(rawdata).tobytes()

        def load(self, filename_re, filename_im=None, imsize=[512, 512]):
                image_re = mpimg.imread(filename_re)
                image_re = spy.imresize(image_re, imsize)[:,:,0]
                image_re = np.floor(image_re)
                self.image_re = np.uint32(image_re)

                if(filename_im is None):
                        self.image_im = np.zeros(imsize)
                else:
                        image_im = mpimg.imread(filename_im)
                        image_im = spy.imresize(image_im, imsize)[:,:,0]
                        image_im = np.floor(image_im)
                        self.image_im = np.uint32(image_im)

        def __str__(self):
                # shift values and convert to 32 bit integer
                if (self.image_re is not None):                
                        image_re = self.image_re * np.power(2, self.shift)
                        image_re = np.floor(image_re)
                        image_re = np.uint32(image_re)

                        image_im = self.image_im * np.power(2, self.shift)
                        image_im = np.floor(image_im)
                        image_im = np.uint32(image_im)
                
                        y_re = image_re.reshape([1, image_re.shape[0]*image_re.shape[1]])
                        y_im = image_im.reshape([1, image_im.shape[0]*image_im.shape[1]])

                if(self.cmplx_out == True):
                        # build complex vales with imaginary part zero
                        c = np.empty((y_re.size+y_im.size,), dtype=y_re.dtype)
                        c[0::2] = y_re
                        c[1::2] = y_im
                        return self.gen_rearrange(c)
                else:
                        return self.gen_reaarange(y_re)

        def show(self, cmap='gray', imsize=[512, 512]):
                plt.subplot(1, 2, 1)
                plt.imshow(np.float32(self.image_re), cmap)
                
                plt.subplot(1, 2, 2)
                plt.imshow(np.float32(self.image_im), cmap)
                
                plt.show()

        def show_abs(self, cmap='gray', imsize=[512, 512]):
                plt.imshow(abs(self.image_re + 1j * self.image_im), cmap)
                plt.show()

        def show_re(self, cmap='gray', imsize=[512, 512]):
                plt.imshow(self.image_re, cmap)
                plt.show()

        def show_im(self, cmap='gray', imsize=[512, 512]):
                plt.imshow(self.image_im, cmap)
                plt.show()

        def black(self, imsize=[512, 512]):
                self.image_re = np.zeros(imsize)
                self.image_im = np.zeros(imsize)

        def white(self, imsize=[512, 512]):
                self.image_re = np.ones(imsize)
                self.image_im = np.ones(imsize)

        def circ_mask(self, radius, imsize=[512, 512]):
                u,v = imsize
                u = u/2
                v = v/2
                mask_re = np.ones(imsize)
                self.image_im = np.zeros(imsize)
                y,x = np.ogrid[-imsize[0]/2:imsize[0]/2,-imsize[1]/2:imsize[1]/2]
                mask = x**2 + y**2 <= radius**2
                mask_re[mask] = 0
                #self.image_im[mask] = 1
                self.image_re = np.concatenate((mask_re[u:,v:], mask_re[u:,0:v]), axis=1)
                image_tmp = np.concatenate((mask_re[0:u,v:], mask_re[0:u,0:v]), axis=1)
                self.image_re = np.concatenate((self.image_re, image_tmp), axis=0)

                #self.image_im = np.concatenate((self.image_im, self.image_im), axis=0)
                #self.image_im = np.concatenate((self.image_im, self.image_im), axis=1)

        def pattern(self, imsize=[512, 512]):
      
                # build complex values with imaginary part zero
                self.image_re = np.empty(imsize)
                self.image_re[0::2] = 1.0
                self.image_re[1::2] = 0.0
                self.image_re.transpose()

                self.image_im = np.zeros(imsize)

        def fits(self, filename, shift=0, imsize=[512, 512]):
                hdu_list = pyfits.open(filename)
                self.image_re = hdu_list[0].data
                self.image_re = spy.imresize(self.image, imsize)[:,:]

                self.image_im = np.zeros(imsize)

        def set_image(self, data, imsize=[512, 512]):
                data = Image.gen_rearrange(data)
                c = np.frombuffer(data, np.int32)
                y = np.empty(imsize[0]*imsize[1], np.complex)
                y.real = c[0::2]
                y.imag = 1 * c[1::2]
                
                y = y.reshape(imsize)
                self.image_re = y.real / np.power(2, self.shift)
                self.image_im = y.imag / np.power(2, self.shift)
                #print(by.min())
                #print(by.max())
#                plt.subplot(2, 1, 1)
#                plt.imshow(by.real)
#                plt.subplot(2, 1, 2)
#                plt.plot(by[0, ::].real)
#                plt.show()
                #by = by.astype(np.complex)
                #by = 255 * by / by.max()
                #mpimg.imsave('image_real.png', by.real, cmap='gray')
                #mpimg.imsave('image_image.png', by.imag, cmap='gray')
                                
        def sine(self, freq, imsize=[512, 512], phase=0, offset=0, vertical=True):
                # generate sine test vector
                t = np.linspace(0, 2*np.pi, imsize[0])
                y = np.zeros(len(t))
                for i in range(len(freq)):
                        y += (1.0 + np.sin(freq[i] * (t + phase))) / len(freq) + offset

                self.image_re = np.empty(imsize)
                self.image_re[::, ::] = 1024 * y
                self.image_im = np.zeros(imsize) + offset

                if(vertical == False):
                        self.image_re = self.image_re.transpose()

        def __add__(self, other):
                result = Image(cmplx_out = self.cmplx_out | other.cmplx_out)
                result.image_re = np.floor(self.image_re) + np.floor(other.image_re)
                result.image_im = np.floor(self.image_im) + np.floor(other.image_im)
                return result

        def __sub__(self, other):
                result = Image(cmplx_out = self.cmplx_out | other.cmplx_out)
                result.image_re = np.floor(self.image_re) - np.floor(other.image_re)
                result.image_im = np.floor(self.image_im) - np.floor(other.image_im)
                return result

        def __mul__(self, other):
                result = Image(cmplx_out = self.cmplx_out | other.cmplx_out)
                result.image_re = np.floor(self.image_re) * np.floor(other.image_re)
                result.image_im = np.floor(self.image_im) * np.floor(other.image_im)
                return result

        def __div__(self, other):
                result = Image(cmplx_out = self.cmplx_out | other.cmplx_out)
                result.image_re = np.floor(self.image_re) / np.floor(other.image_re)
                result.image_im = np.floor(self.image_im) / np.floor(other.image_im)
                
                return result

        def cmult(self, other):
                result = Image(cmplx_out = self.cmplx_out | other.cmplx_out)
                result.image_re = np.floor(self.image_re) * np.floor(other.image_re) - \
                                  np.floor(self.image_im) * np.floor(other.image_im)

                result.image_im = np.floor(self.image_re) * np.floor(other.image_im) + \
                                  np.floor(self.image_im) * np.floor(other.image_re)
                return result

        def fft(self, axis=1):
                result = Image(cmplx_out = self.cmplx_out)

                image_fft = np.fft.fft(self.image_re + 1j * self.image_im, axis=axis)
                result.image_re = np.floor(image_fft.real)
                result.image_im = np.floor(image_fft.imag)
                return result

        def ifft(self, axis=1):
                result = Image(cmplx_out = self.cmplx_out)

                image_fft = np.fft.ifft(self.image_re + 1j * self.image_im, axis=axis)
                result.image_re = np.floor(image_fft.real)
                result.image_im = np.floor(image_fft.imag)

                return result

        def fft2(self):
                result = Image(cmplx_out = self.cmplx_out)

                image_fft = np.fft.fft2(self.image_re + 1j * self.image_im)
                result.image_re = np.floor(image_fft.real)
                result.image_im = np.floor(image_fft.imag)
                return result

        def ifft2(self):
                result = Image(cmplx_out = self.cmplx_out)

                image_fft = np.fft.ifft2(self.image_re + 1j * self.image_im)
                result.image_re = np.floor(image_fft.real)
                result.image_im = np.floor(image_fft.imag)
                return result

#        def ret_image32(self, data):
#                rawdata = bytearray(data)
#                for i in range(0, len(rawdata), 4):
#                        temp = rawdata[i:i+4]
#                        rawdata[i+0] = temp[3]
#                        rawdata[i+1] = temp[2]
#                        rawdata[i+2] = temp[1]
#                        rawdata[i+3] = temp[0]
#                c = np.frombuffer(rawdata, np.uint32)
                #d = np.empty([2048* 2048])
                #print(len(d))
#                c = c.astype(np.float32)
#                d = c.reshape([2048, 2048])
#                print(d[0,0:4])
                #d = d / d.max()
                
                #plt.imshow(d)
                #plt.show()

#        def gen_chlink_pattern(self):
#                y = np.linspace(0, 2047, 2048)
#                z = np.empty([2048, 2048])
#                z[::, ::] = y
#
#                self.gen_chlink_data(z)

#       def gen_chlink_data(self, pattern):
#                data = np.floor(pattern)
#                data = (np.uint16(data) & 0xfff) << 2
#                payload = bytearray(data)

#                f = open('chlink_pattern.raw', 'wb')
#                f.write(payload)
#                f.close()

#        def import_chlink_pattern(self):
#                f = open('chlink_rcv_pattern.raw', 'rb')
#                data = f.read()
#                f.close()

                
        
               
