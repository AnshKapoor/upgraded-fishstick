from SpaceWire import *
from tests import *
from sophilib import Jtag
from sophilib import Nand
from sophilib import Preproc
from sophilib import RamFs
from sophilib import Image
from sophilib import SoCWire, PathSetup

import numpy as np
import matplotlib.pyplot as plt
import scipy.misc as spy
import matplotlib.image as mpimg

class Test_Preproc():

	def __init__(self, spw):
                self.spw = spw
                self.jtag = Jtag(spw)
                self.preproc = Preproc(spw)
                self.ramfs = RamFs(spw)
                
        def test(self):
                socwire = SoCWire(self.spw)
                self.jtag.config('bitfiles/preproc_fresh.bit', 2)
                socwire.pathtable_setup(PathSetup.Preproc)
                # Test FFT operator
                #self.test_fft()

                # Test arithmetic operator (add, sub and mult)
                #self.test_arith()

                # Test complex multiplication
                #self.test_cmult()

                # Test division
                self.test_div()

                #self.ref_filt()
                #self.test_filt()

        def test_arith(self):
                #image1.load('testdata/QM2.png')
                #image2.load('testdata/QM2.png')
                #image.black()

                # Generate image 1 with vertical sine pattern
                image1 = Image(cmplx_out=True)
                #image1.sine([5,10,20])
                image1.load('testdata/QM2.png', 'testdata/sin8d.gif')
                #image1.show()

                # Upload and store image 1
                self.preproc.store_direct(str(image1))

                # Generate image 2 with horizontal sine pattern
                image2 = Image(cmplx_out=True)
                #image2.sine([5,10,20], vertical=False)
                #image2.load('testdata/sin8d.gif', 'testdata/QM2.png')
                image2.circ_mask(100)
                # Upload and store image 2
                self.preproc.store_direct(str(image2), 0x40000)

                # Execute operations
                self.preproc.add(0x00000, 0x40000, 0x080000, 0x040000)
                self.preproc.sub(0x00000, 0x40000, 0x100000, 0x040000)
                self.preproc.mult(0x00000, 0x40000, 0x140000, 0x040000)
                self.preproc.cmult(0x00000, 0x40000, 0x180000, 0x040000)
                self.preproc.div(0x00000, 0x40000, 0x200000, 0x040000)

                # Calculate reference results
                image_add = image1 + image2
                image_sub = image1 - image2
                image_mult = image1 * image2
                image_cmult = image1.cmult(image2)
                image_div = image1 / image2
                
                image_cmult.show()
                
                # Load add result...
                data_add = self.preproc.load_direct(0x080000, 0x40000)

                # ... and compare
                if (data_add == str(image_add)):
                        print('Addition operator passed successfully')
                else:
                        print('Addition operator failed')

                # Load sub result...
                data_sub = self.preproc.load_direct(0x100000, 0x40000)

                # ... and compare
                if (data_sub == str(image_sub)):
                        print('Substraction operator passed successfully')
                else:
                        print('Substraction operator failed')

                # Load mult result...
                data_mult = self.preproc.load_direct(0x140000, 0x40000)

                # ... and compare
                if (data_mult == str(image_mult)):
                        print('Multiplication operator passed successfully')
                else:
                        print('Multiplication operator failed')
                
                # Load cmult result...
                data_cmult = self.preproc.load_direct(0x180000, 0x40000)

                # ... and compare
                if (data_cmult == str(image_cmult)):
                        print('Complex multiplication operator passed successfully')
                else:
                        print('Complex multiplication operator failed')

                # Load div result...
                data_div = self.preproc.load_direct(0x200000, 0x40000)

                # ... and compare
                if (data_div == str(image_div)):
                        print('Division operator passed successfully')
                else:
                        print('Division operator failed')
                        
                #image1.show()
                #image2.show()
                #image3.show()
                #print(data == str(image3))
                image4 = Image(cmplx_out=True)
                image4.set_image(data_cmult)
              
               
                image4.show()
                image5 = image_cmult - image4
                image5.show()

        def test_fft(self):
                image1 = Image(cmplx_out=True)
                image1.load('testdata/QM2.png')

                # Upload and store image 1
                self.preproc.store_direct(str(image1), 0x00000)
                
                self.preproc.fft(0x000000, 0x040000, 512, 512)
                self.preproc.fft(0x040000, 0x080000, 512, 512, True)

                self.preproc.ifft(0x080000, 0x0c0000, 512, 512, True)
                self.preproc.ifft(0x0c0000, 0x100000, 512, 512)
                
                # Load FFT result...
                data_fft = self.preproc.load_direct(0x100000, 0x40000)

                image_fft = Image(cmplx_out=True)
                image_fft.set_image(data_fft)
                #image_fft.circ_mask(32)

                image_fft.show()

        def ref_filt(self):
                image1 = Image(cmplx_out=True)
                image1.load('testdata/QM2.png', None, [2048,2048])
                #image1.sine([5,10,20])
                #image1.show()
                
                image_mask = Image(cmplx_out=True)
                image_mask.circ_mask(400, [2048,2048])
                image_mask.show()

                ref_fft = np.fft.fft(image1.image_re)
                ref_fft2 = np.fft.fft(ref_fft, axis=0)

                #ref_fft = np.fft.fftshift(ref_fft)
                
                imref_fft = Image(cmplx_out=True)
                imref_fft.image_re = np.int32(np.floor(ref_fft2.real))
                imref_fft.image_im = np.int32(np.floor(ref_fft2.imag))

                #imref_fft.show()
                im_filt = imref_fft.cmult(image_mask)
                im_filt.show()

                re_fft = im_filt.image_re + 1j * im_filt.image_im
                #re_fft = np.fft.ifftshift(re_fft)
                im_rest2 = np.fft.ifft(re_fft, axis=0)
                im_rest = np.fft.ifft(im_rest2)

                im_rest_fft = Image(cmplx_out=True)
                im_rest_fft.image_re = abs(im_rest)
                im_rest_fft.image_im = im_rest.imag
                im_rest_fft.show()
                #imref_fft.show()
                
        def test_div(self):
                # Generate image 1 with vertical sine pattern
                image1 = Image(cmplx_out=True)
                image1.sine([5,10,20])
                image1.show()

                # Upload and store image 1
                self.preproc.store_direct(str(image1))

                # Generate image 2 with horizontal sine pattern
                image2 = Image(cmplx_out=True)
                image2.sine([5,10,20], phase=0, offset=1, vertical=False)
                image2.show()
                
                # Upload and store image 2
                self.preproc.store_direct(str(image2), 0x40000)

                # Execute operations
                self.preproc.div(0x40000, 0x00000, 0x200000, 0x040000)

                # Calculate reference results
                image_div = image1 / image2
                
                image_div.show()

                # Load div result...
                data_div = self.preproc.load_direct(0x200000, 0x40000)
                imld_div = Image(cmplx_out=True)
                imld_div.set_image(data_div, [512, 512])
                imld_div.show()
                
                # ... and compare
                if (data_div == str(image_div)):
                        print('Division operator passed successfully')
                else:
                        print('Division operator failed')
                        image5 = image_div - imld_div
                        image5.show()
             
        def test_filt(self):
                image1 = Image(cmplx_out=True)
                image1.load('testdata/QM2.png', None, [2048, 2048])
                #image1.sine([5,10,20])
                #image1.show()
                
                image_mask = Image(cmplx_out=True)
                image_mask.circ_mask(100, [2048, 2048])
                #image_mask.show()
                
                im_fft_h = image1.fft()
                im_fft = im_fft_h.fft(axis=0)
                #im_fft.show()
                
                im_filt = im_fft.cmult(image_mask)
                #im_filt.show()

                im_rest_h = im_filt.ifft(axis=0)
                im_rest = im_rest_h.ifft()
                im_rest.show()
                
                # Upload and store image 1
                for i in range(4):
                        self.preproc.store_direct(str(image1)[i*8*1024*1024:(i+1)*8*1024*1024], i*1024*1024)

                # Upload and store mask
                for i in range(4):
                        self.preproc.store_direct(str(image_mask)[i*8*1024*1024:(i+1)*8*1024*1024], 4*1024*1024+i*1024*1024)
                #self.preproc.store_direct(str(image_mask), 0x400000)
                
                self.preproc.fft(0x0000000, 0x0800000, 2048, 2048)
                self.preproc.fft(0x0800000, 0x0c00000, 2048, 2048, True)
                
                #self.preproc.cmult(0x0400000, 0x0c00000, 0x1000000, 0x400000)
                
                self.preproc.ifft(0x0c00000, 0x1400000, 2048, 2048, True)
                self.preproc.ifft(0x1400000, 0x1800000, 2048, 2048)
                
                # Load cmult result...
                #data_cmult = self.preproc.load_direct(0x100000, 0x40000)
                
                #image_cmult = Image(cmplx_out=True)
                #image_cmult.set_image(data_cmult)

                #differ = image_cmult - im_filt
                #differ.show()
                #image_cmult.show_abs()
                
                # Load FFT result...
                data_fft = ''
                for i in range(4):
                        data_fft += self.preproc.load_direct(0x0800000+i*1024*1024, 1024*1024)#0x400000)

                image_fft = Image(cmplx_out=True)
                image_fft.set_image(data_fft, [2048, 2048])

                image_fft.show_abs()
                """
                plt.subplot(4, 1, 1)
                plt.plot(np.float32(im_fft_h.image_re[0,:]))
                
                plt.subplot(4, 1, 2)
                plt.plot(np.float32(im_fft_h.image_im[0,:]))

                plt.subplot(4, 1, 3)
                plt.plot(np.float32(image_fft.image_re[0,:]))

                plt.subplot(4, 1, 4)
                plt.plot(np.float32(image_fft.image_im[0,:]))
                
                plt.show()
                """
                 # ... and compare
                #if (data_fft == str(imref_fft)):
                #        print('FFT operator passed successfully')
                #else:
                #        print('FFT operator failed')
                        
                #image5 = image_fft - imref_fft

                #print(image5.image_re.min())
                #print(image5.image_re.max())
                #print(image5.image_im.min())
                #print(image5.image_im.max())
                
                #image5.show()
                
                
                
