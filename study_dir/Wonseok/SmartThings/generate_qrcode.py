# Generate device QR code
import qrcode

mnid = '' 
onboardingId = ''
serialNumber = ''
qrUrl = 'https://qr.samsungiots.com/?m=' + mnid + '&s=' + onboardingId + '&r=' + serialNumber
img = qrcode.make(qrUrl)
img.save(serialNumber + '.png')
qrcode.QRCode(box_size=10, border=4)
