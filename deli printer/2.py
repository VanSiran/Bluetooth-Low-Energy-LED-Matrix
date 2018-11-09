from ctypes import windll, Structure, c_char_p
from ctypes.wintypes import HANDLE, PHANDLE, DWORD, PINT, LPBYTE, LPDWORD, BOOL, LPSTR, LPVOID
import code128
from PIL import Image, ImageDraw
import PIL.ImageFont as ImageFont

PRNs = b'''<xpml><page quantity='0' pitch='80.1 mm'></xpml>SIZE 100.0 mm, 80.1 mm\r
DIRECTION 0,0\r
REFERENCE 0,0\r
OFFSET 0\r
SET PEEL OFF\r
SET CUTTER OFF\r
<xpml></page></xpml><xpml><page quantity='1' pitch='80.1 mm'></xpml>SET TEAR ON\r
CLS\r
'''
PRNe = b'''\r
PRINT 1,1\r
<xpml></page></xpml><xpml><end/></xpml>'''

class DOC_INFO_1(Structure):
    _fields_ = [('pDocName', c_char_p),
                ('pOutputFile', c_char_p),
                ('pDatatype', c_char_p),]

class PRINTER_INFO_2(Structure):
    _fields_ = [('pServerName', LPSTR),
                ('pPrinterName', LPSTR),
                ('pShareName', LPSTR),
                ('pPortName', LPSTR),
                ('pDriverName', LPSTR),
                ('pComment', LPSTR),
                ('pLocation', LPSTR),
                ('pDevMode', LPVOID),
                ('pSepFile', LPSTR),
                ('pPrintProcessor', LPSTR),
                ('pDatatype', LPSTR),
                ('pParameters', LPSTR),
                ('pSecurityDescriptor', LPVOID),
                ('Attributes', DWORD),
                ('Priority', DWORD),
                ('DefaultPriority', DWORD),
                ('StartTime', DWORD),
                ('UntilTime', DWORD),
                ('Status', DWORD),
                ('cJobs', DWORD),
                ('AveragePPM', DWORD),]
    
winspool = windll.LoadLibrary('C:/windows/system32/winspool.drv')


height = 30
thickness = 2
xcord = 500
ycord = 600
code = '20132501'
try:
    hPrinter = HANDLE()
    if winspool.OpenPrinterA(c_char_p(b'Deli DL-888D'), PHANDLE(hPrinter), c_char_p(None)) == 0:
        raise Exception('Error: Cant open printer.')

    printerInfo = PRINTER_INFO_2()
    num2 = DWORD(0)
    print(winspool.GetPrinterA(hPrinter, 2, LPDWORD(printerInfo), DWORD(2080), LPDWORD(num2)) == 0, printerInfo.cJobs, num2)
    print(printerInfo.Status)

    docInfo = DOC_INFO_1(c_char_p(b'IMEI'), c_char_p(None), c_char_p(b'RAW'))
    if winspool.StartDocPrinterA(hPrinter, DWORD(1), LPBYTE(docInfo)) == 0:
        winspool.ClosePrinter(hPrinter)
        raise Exception('Error: Cant open doc.')

    if winspool.StartPagePrinter(hPrinter) == 0:
        winspool.EndDocPrinter(hPrinter)
        winspool.ClosePrinter(hPrinter)
        raise Exception('Error: Cant open page.')


    image = code128.image(code, height=height, thickness=thickness).tobytes()
    content = 'BITMAP {},{},{},{},1,'.format(xcord, ycord, len(image)//height, height).encode('ascii') + image

    ##img=Image.new(mode='1',size=(336,40),color='white')
    ##draw=ImageDraw.Draw(img,'1')
    ##font=ImageFont.truetype("arial.ttf", 40)
    ##draw.text([0,0], '12345', font=font)
    ##content = b"BITMAP 59,98,42,40,1," + img.tobytes()
    content = PRNs + content + PRNe

    wl = DWORD()
    if winspool.WritePrinter(hPrinter, c_char_p(content), DWORD(len(content)), LPDWORD(wl)) == 0 \
        or wl.value == 0:
        winspool.EndPagePrinter(hPrinter)
        winspool.EndDocPrinter(hPrinter)
        winspool.ClosePrinter(hPrinter)
        raise Exception('Error: Cant print.')
    winspool.EndPagePrinter(hPrinter)
    winspool.EndDocPrinter(hPrinter)
    winspool.ClosePrinter(hPrinter)
    print("Written {} bytes." .format(wl.value))
except Exception as e:
    print(str(e))
