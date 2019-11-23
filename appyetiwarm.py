from flask import Flask, render_template, redirect, url_for, request
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import hashlib
import os
import subprocess
import json
import cv2
from qrtools.qrtools import QR
from pyzbar.pyzbar import decode
from PIL import Image
import random
import qrcode
app = Flask(__name__)
home = os.getenv("HOME")
rpcpsw = str(random.randrange(0,1000000))
subprocess.call(['sudo apt-get update'],shell=True)
if not (os.path.exists(home + "/.bitcoin")):
    subprocess.call(['mkdir ~/.bitcoin'],shell=True)
else:
    subprocess.call(['rm ~/.bitcoin/bitcoin.conf'],shell=True)
subprocess.call('echo "server=1\nrpcport=8332\nrpcuser=rpcuser\nrpcpassword='+rpcpsw+'" >> '+home+'/.bitcoin/bitcoin.conf', shell=True)

### VARIBALES START
settings = {
    "rpc_username": "rpcuser",
    "rpc_password": rpcpsw,
    "rpc_host": "127.0.0.1",
    "rpc_port": 8332,
    "address_chunk": 100
}
wallet_template = "http://{rpc_username}:{rpc_password}@{rpc_host}:{rpc_port}/wallet/{wallet_name}"
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
base_count = len(BASE58_ALPHABET)
privkeylist = []
xprivlist = []
firstqrcode = 0
secondqrcode = 0
error = None
thirdqrcode = 0
privkeycount = 0
firstqrname = None
secondqrname = None
thirdqrname = None
firsttrans = None
secondtrans = None
thirdtrans = None
utxoresponse = None
pubdesc = None
adrlist = []
transnum = 0
progress = 0
utxo = None
switcher = {
    "1": "ONE",
    "2": "TWO",
    "3": "THREE",
    "4": "FOUR",
    "5": "FIVE",
    "6": "SIX",
    "7": "SEVEN",
    "8": "EIGHT",
    "9": "NINE",
    "A": "ALFA",
    "B": "BRAVO",
    "C": "CHARLIE",
    "D": "DELTA",
    "E": "ECHO",
    "F": "FOXTROT",
    "G": "GOLF",
    "H": "HOTEL",
    "I": "INDIA",
    "J": "JULIETT",
    "K": "KILO",
    "L": "LIMA",
    "M": "MIKE",
    "N": "NOVEMBER",
    "O": "OSCAR",
    "P": "PAPA",
    "Q": "QUEBEC",
    "R": "ROMEO",
    "S": "SIERRA",
    "T": "TANGO",
    "U": "UNIFORM",
    "V": "VICTOR",
    "W": "WHISKEY",
    "X": "X-RAY",
    "Y": "YANKEE",
    "Z": "ZULU",
    "a": "alfa",
    "b": "bravo",
    "c": "charlie",
    "d": "delta",
    "e": "echo",
    "f": "foxtrot",
    "g": "golf",
    "h": "hotel",
    "i": "india",
    "j": "juliett",
    "k": "kilo",
    "l": "lima",
    "m": "mike",
    "n": "november",
    "o": "oscar",
    "p": "papa",
    "q": "quebec",
    "r": "romeo",
    "s": "sierra",
    "t": "tango",
    "u": "uniform",
    "v": "victor",
    "w": "whiskey",
    "x": "x-ray",
    "y": "yankee",
    "z": "zulu",
    "ONE": "1",
    "TWO": "2",
    "THREE": "3",
    "FOUR": "4",
    "FIVE": "5",
    "SIX": "6",
    "SEVEN": "7",
    "EIGHT": "8",
    "NINE": "9",
    "ALFA": "A",
    "BRAVO": "B",
    "CHARLIE": "C",
    "DELTA": "D",
    "ECHO": "E",
    "FOXTROT": "F",
    "GOLF": "G",
    "HOTEL": "H",
    "INDIA": "I",
    "JULIETT": "J",
    "KILO": "K",
    "LIMA": "L",
    "MIKE": "M",
    "NOVEMBER": "N",
    "OSCAR": "O",
    "PAPA": "P",
    "QUEBEC": "Q",
    "ROMEO": "R",
    "SIERRA": "S",
    "TANGO": "T",
    "UNIFORM": "U",
    "VICTOR": "V",
    "WHISKEY": "W",
    "X-RAY": "X",
    "YANKEE": "Y",
    "ZULU": "Z",
    "alfa": "a",
    "bravo": "b",
    "charlie": "c",
    "delta": "d",
    "echo": "e",
    "foxtrot": "f",
    "golf": "g",
    "hotel": "h",
    "india": "i",
    "juliett": "j",
    "kilo": "k",
    "lima": "l",
    "mike": "m",
    "november": "n",
    "oscar": "o",
    "papa": "p",
    "quebec": "q",
    "romeo": "r",
    "sierra": "s",
    "tango": "t",
    "uniform": "u",
    "victor": "v",
    "whiskey": "w",
    "x-ray": "x",
    "yankee": "y",
    "zulu": "z"
}
### VARIBALES STOP


### FUNCTIONS START

def BTCprogress():
    response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli getblockchaininfo'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if not (len(response[0]) == 0):
        bitcoinprogress = json.loads(response[0])['verificationprogress']
        bitcoinprogress = bitcoinprogress * 100
        bitcoinprogress = round(bitcoinprogress, 3)
    else:
        print("error response: "+ str(response[1]))
        bitcoinprogress = 0
    return bitcoinprogress

def RPC():
    name = 'username'
    wallet_name = ''
    uri = wallet_template.format(**settings, wallet_name=wallet_name)
    rpc = AuthServiceProxy(uri, timeout=600)  # 1 minute timeout
    return rpc

def encode_base58(s):
    count = 0
    for c in s:
        if c == 0:
            count += 1
        else:
            break
    num = int.from_bytes(s, 'big')
    prefix = '1' * count
    result = ''
    while num > 0:
        num, mod = divmod(num, 58)
        result = BASE58_ALPHABET[mod] + result
    return prefix + result

def decode_base58(s):
    decoded = 0
    multi = 1
    s = s[::-1]
    for char in s:
        decoded += multi * BASE58_ALPHABET.index(char)
        multi = multi * base_count
    return decoded

def hash256(s):
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

def wif(pk):
    prefix = b"\x80"
    suffix = b'\x01'
    extended_key = prefix + pk + suffix
    assert(len(extended_key) == 33 or len(extended_key) == 34)
    final_key = extended_key + hash256(extended_key)[:4]
    WIF = encode_base58(final_key)
    return WIF

def padhex(hex):
    if len(hex) == 64:
        return hex
    else:
        return padhex('0' + hex)

def BinaryToWIF(binary):
    assert(len(binary) == 256)
    key = hex(int(binary, 2)).replace('0x', "")
    padkey = padhex(key)
    assert(int(padkey, 16) == int(key,16))
    return wif(bytes.fromhex(padkey))

def PassphraseListToWIF(passphraselist):
    Privkey = ''
    for i in range(len(passphraselist)):
        Privkey += switcher.get(str(passphraselist[i]))
    return Privkey

def WIFToPassphraseList(privkeywif):
    passphraselist = []
    for i in range(len(privkeywif)):
        passphraselist.append(switcher.get(str(privkeywif[i])))
    return passphraselist

def xor(x, y):
    return '{1:0{0}b}'.format(len(x), int(x, 2) ^ int(y, 2))

### FUNCTIONS STOP

@app.route("/", methods=['GET', 'POST'])
def step01():
    if request.method == 'GET':
        return redirect('/menu')
    return render_template('redirect.html')

### open bitcoin
@app.route("/step06", methods=['GET', 'POST'])
def step06():
    if request.method == 'POST':
        subprocess.Popen('~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-qt -proxy=127.0.0.1:9050',shell=True,start_new_session=True)
        return redirect('/step07')
    return render_template('YWstep06.html')
#finish open bitcoin
@app.route("/step07", methods=['GET', 'POST'])
def step07():
    global progress
    if request.method == 'GET':
        progress = BTCprogress()
    if request.method == 'POST':
        if progress >= 99.9:
            return redirect('/menu')
        else:
            return redirect('/step07')
    return render_template('YWstep07.html', progress=progress)

@app.route("/menu", methods=['GET', 'POST'])
def menu():
    if request.method == 'POST':
        if request.form['option'] == 'recovery':
            return redirect('/Recovery/step08')
        else:
            return redirect('/step08')
    return render_template('menu.html')

#randomise priv key and get xprivs
@app.route("/step08", methods=['GET', 'POST'])
def step08():
    global privkeylist
    global privkeycount
    global xprivlist
    global pubdesc
    if request.method == 'POST':
        if request.form['skip'] == 'skip':
            privkeylisttemp = []
            for i in range(1,8):
                rpc = RPC()
                adr = rpc.getnewaddress()
                newprivkey = rpc.dumpprivkey(adr)
                binary = bin(decode_base58(newprivkey))[2:][8:-40]
                newbinary = '1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111'
                WIF = BinaryToWIF(xor(binary,newbinary))
                privkeylisttemp.append(WIF)
            privkeycount = 0
            privkeylist = privkeylisttemp
        else:
            privkeylisttemp = []
            for i in range(1,8):
                rpc = RPC()
                adr = rpc.getnewaddress()
                newprivkey = rpc.dumpprivkey(adr)
                binary = bin(decode_base58(newprivkey))[2:][8:-40]
                WIF = BinaryToWIF(xor(binary,request.form['binary' + str(i)]))
                privkeylisttemp.append(WIF)
            privkeycount = 0
            privkeylist = privkeylisttemp
        for i in range(0,7):
            home = os.getenv('HOME')
            pathtwo = home + '/blank' + str(i)
            path = home + '/full' + str(i)
            response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli createwallet "full'+str(i)+'"'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli loadwallet "full'+str(i)+'"'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli -rpcwallet=full'+str(i)+' sethdseed false "'+privkeylist[i]+'"'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            if not (len(response[1]) == 0): 
                print(response)
                return "error response from sethdseed: " + str(response[1]) + '\n' + '~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli -rpcwallet=full'+str(i)+' sethdseed false "'+privkeylist[i]+'"'
            response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli -rpcwallet=full'+str(i)+' dumpwallet "full'+str(i)+'"'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            wallet = open(path,'r')
            wallet.readline()
            wallet.readline()
            wallet.readline()
            wallet.readline()
            wallet.readline()
            privkeyline = wallet.readline()
            privkeyline = privkeyline.split(" ")[4][:-1]
            xprivlist.append(privkeyline)
        addresses = []
        checksum = None
        response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli getdescriptorinfo "wsh(multi(3,'+xprivlist[0]+'/*,'+xprivlist[1]+'/*,'+xprivlist[2]+'/*,'+xprivlist[3]+'/*,'+xprivlist[4]+'/*,'+xprivlist[5]+'/*,'+xprivlist[6]+'/*))"'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        if not (len(response[0]) == 0): 
            response = json.loads(response[0].decode("utf-8"))
        else:
            print(response)
            return "error response from getdescriptorinfo: " + str(response[1]) + '\n' + '~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli getdescriptorinfo "wsh(multi(3,'+xprivlist[0]+'/*,'+xprivlist[1]+'/*,'+xprivlist[2]+'/*,'+xprivlist[3]+'/*,'+xprivlist[4]+'/*,'+xprivlist[5]+'/*,'+xprivlist[6]+'/*))"'
        checksum = response["checksum"]
        pubdesc = response["descriptor"]
        return redirect('/step09')
    return render_template('YWstep08.html')
#display seeds
@app.route('/step0915', methods=['GET', 'POST'])
def step0915():
    global privkeylist
    global privkeycount
    if request.method == 'GET':
        privkey = privkeylist[privkeycount]
        passphraselist = WIFToPassphraseList(privkey)
    if request.method == 'POST':
        home = os.getenv('HOME')
        path = home + '/Documents'
        subprocess.call('rm '+path+'/seed'+str(privkeycount + 1)+'.txt', shell=True)
        subprocess.call('touch '+path+'/seed'+str(privkeycount + 1)+'.txt', shell=True)
        file = ''
        for i in range(0,13):
            file = file + request.form['displayrow' + str(i+1)] + '\n'
        subprocess.call('echo "'+file+'" >> '+path+'/seed'+str(privkeycount + 1)+'.txt', shell=True)
        privkeycount = privkeycount + 1
        if (privkeycount == 7):
            privkeycount = 0
            return redirect('/step1521')
        else:
            return redirect('/step0915')
    return render_template('YWstep0915.html', PPL=passphraselist, x=privkeycount + 1, i=privkeycount + 25)
#confirm privkey
@app.route('/step1521', methods=['GET', 'POST'])
def step1521():
    global privkeylist
    global xprivlist
    global privkeycount
    global error
    if request.method == 'POST':
        privkey = privkeylist[privkeycount]
        passphraselist = WIFToPassphraseList(privkey)
        privkeylisttoconfirm = []
        for i in range(1,14):
            inputlist = request.form['row' + str(i)]
            inputlist = inputlist.split(' ')
            inputlist = inputlist[0:4]
            privkeylisttoconfirm.append(inputlist[0])
            privkeylisttoconfirm.append(inputlist[1])
            privkeylisttoconfirm.append(inputlist[2])
            privkeylisttoconfirm.append(inputlist[3])
        if privkeylisttoconfirm == passphraselist:
            error = None
            privkeycount = privkeycount + 1
            if (privkeycount >= 7):
                privkeycount = 7
                newxprivlist = []
                for i in range(0,7):
                    rpc = RPC()
                    home = os.getenv('HOME')
                    path = home + '/full' + str(i)
                    response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli createwallet "full'+str(i)+'" false true'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                    response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli loadwallet "full'+str(i)+'"'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                    response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli -rpcwallet=full'+str(i)+' sethdseed false "'+privkeylist[i]+'"'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                    if not (len(response[1]) == 0): 
                        print(response)
                        return "error response from sethdseed: " + str(response[1]) + '\n' + '~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli -rpcwallet=full'+str(i)+' sethdseed false "'+privkeylist[i]+'"'
                    response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli -rpcwallet=full'+str(i)+' dumpwallet "full'+str(i)+'"'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                    wallet = open(path,'r')
                    wallet.readline()
                    wallet.readline()
                    wallet.readline()
                    wallet.readline()
                    wallet.readline()
                    privkeyline = wallet.readline()
                    privkeyline = privkeyline.split(" ")[4][:-1]
                    newxprivlist.append(privkeyline)
                    if not xprivlist[i] == newxprivlist[i]:
                        privkeycount = 0
                        privkeylist = []
                        error = 'You have imported your seeds correctly but your xprivs do not match: This means that you either do not have bitcoin running or its initial block download mode. Another issue is that you have a wallet folder or wallet dump file that was not deleted before starting this step.'
                        return redirect('/step1521')
                return redirect('/step22')
            else:
                return redirect('/step1521')
        else:
            error = 'You enterd the private key incorrectly but the checksums are correct please try agian. This means you probably inputed a valid seed, but not your seed ' +str(privkeycount + 1)+' seed.'
    return render_template('YWstep1521.html', x=privkeycount + 1, error=error,i=privkeycount + 35 )
#delete wallet
@app.route("/step22", methods=['GET', 'POST'])
def step22():
    if request.method == 'POST':
        subprocess.call('gnome-terminal -- bash -c "sudo python3 ~/yeticold/utils/deleteallwallets.py; echo "DONE, Close this window.""', shell=True)
        return redirect('/step23')
    return render_template('YWstep22.html')
#reopen bitcoin
@app.route("/step23", methods=['GET', 'POST'])
def step23():
    if request.method == 'POST':
        subprocess.Popen('~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-qt -proxy=127.0.0.1:9050',shell=True,start_new_session=True)
        return redirect('/step24')
    return render_template('YWstep23.html')
#finished reopen bitcoin
@app.route('/step24', methods=['GET', 'POST'])
def step24():
    global progress
    if request.method == 'GET':
        progress = BTCprogress()
    if request.method == 'POST':
        if progress >= 99:
            return redirect('/step25')
        else:
            return redirect('/step24')
    return render_template('YWstep24.html', progress=progress)
#display for print
@app.route("/step25", methods=['GET', 'POST'])
def step25():
    global pubdesc
    if request.method == 'GET':
        randomnum = str(random.randrange(0,1000000))
        firstqrname = randomnum
        qr = qrcode.QRCode(
               version=1,
               error_correction=qrcode.constants.ERROR_CORRECT_L,
               box_size=10,
               border=4,
        )
        qr.add_data(pubdesc)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        home = os.getenv("HOME")
        img.save(home + '/yeticold/static/firstqrcode' + firstqrname + '.png')
        route = url_for('static', filename='firstqrcode' + firstqrname + '.png')
    if request.method == 'POST':
        return redirect('/step26')
    return render_template('YWstep25.html', qrdata=pubdesc, route=route)

@app.route("/step26", methods=['GET', 'POST'])
def step26():
    if request.method == 'POST':
        subprocess.Popen('~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-qt -proxy=127.0.0.1:9050',shell=True,start_new_session=True)
        return redirect('/menue')
    return render_template('YWstep26.html')

###END OF SETUP

#### start recovery

@app.route("/Recovery/step08", methods=['GET', 'POST'])
def Recovery_step08():
    global firstqrcode
    global pubdesc
    if request.method == 'POST':
        if request.form['option'] == 'scannewdesc':
            firstqrcode = subprocess.Popen(['python3 ~/yeticold/utils/scanqrcode.py'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
            firstqrcode = firstqrcode.decode("utf-8")
            pubdesc = firstqrcode[:-2]
        return redirect('/Recovery/step09')
    return render_template('YWRstep08.html', pubdesc=pubdesc)

@app.route("/Recovery/step09", methods=['GET', 'POST'])
def Recovery_step09():
    global firstqrcode
    global pubdesc
    if request.method == 'GET':
        response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli importmulti \'[{ "desc": "'+pubdesc+'", "timestamp": "now", "range": [0,999], "watchonly": false, "label": "test" }]\' \'{"rescan": true}\''],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        print(response)
        if not (len(response[1]) == 0): 
            print(response)
            return "error response from importmulti: " + str(response[1]) + '\n' + '~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli importmulti \'[{ "desc": "'+pubdesc+'", "timestamp": "now", "range": [0,999], "watchonly": false, "label": "test" }]\' \'{"rescan": true}\''
        subprocess.Popen('~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli rescanblockchain 600000',shell=True,start_new_session=True)
    if request.method == 'POST':
        return redirect('/Recovery/step10')
    return render_template('YWRstep09.html')

@app.route("/Recovery/step10", methods=['GET', 'POST'])
def Recovery_step10():
    global addresses
    global color
    global sourceaddress
    if request.method == 'GET':
        subprocess.call(['rm -r ~/yeticold/static/address*'],shell=True)
        addresses = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli deriveaddresses "'+pubdesc+'" "[0,999]"'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        print(addresses)
        if not (len(addresses[0]) == 0): 
            addresses = json.loads(response[0].decode("utf-8"))
        else:
            print(addresses)
            return "error response from deriveaddresses: " + str(addresses[1]) + '\n' + '~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli deriveaddresses "'+pubdesc+'" "[0,999]"'
        for i in range(0, len(addresses)):
            randomnum = str(random.randrange(0,1000000))
            route = url_for('static', filename='address'+randomnum+'.png')
            rpc = RPC()
            testlist = []
            testlist.append(adrlist[i])
            response = rpc.listunspent(0, 9999999, testlist)
            if response == []:
                bal = "0.0000000"
                txid = ''
                vout = 0
            else:
                bal = str(response[0]['amount'])
                txid = str(response[0]['txid'])
                vout = str(response[0]['vout'])
            utxocount = len(response)
            response = rpc.getreceivedbyaddress(adrlist[i])
            if response == 0:
                totalbal = "0.0000000"
            else:
                totalbal = str(response)
            bal = "{:.8f}".format(float(bal))
            address = {}
            address['txid'] = txid
            address['vout'] = vout
            address['utxocount'] = utxocount
            address['address'] = adrlist[i]
            address['balance'] = bal
            address['numbal'] = float(bal)
            address['totalbal'] = totalbal
            address['totalnumbal'] = float(totalbal)
            address['route'] = route
            addresses.append(address)
        addresses.sort(key=lambda x: x['balance'], reverse=True)
        for i in range(0, len(addresses)):
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(addresses[i]['address'])
            qr.make(fit=True)
            color = '#b8daff'
            if (i % 2) == 0:
                color = 'white'
            img = qr.make_image(fill_color="black", back_color=color)
            home = os.getenv("HOME")
            img.save(home + '/yeticold/'+addresses[i]['route'])
    if request.method == 'POST':
        sourceaddress = request.form['address']
        return redirect('/Recovery/step11')
    return render_template('YWRstep10.html', addresses=addresses, len=len(addresses))

@app.route("/Recovery/step11", methods=['GET', 'POST'])
def Recovery_step11():
    global error
    global receipentaddress
    if request.method == 'POST':
        error = None
        receipentaddress = subprocess.Popen(['python3 ~/yeticold/utils/scanqrcode.py'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        receipentaddress = receipentaddress.decode("utf-8").replace('\n', '')
        if (receipentaddress.split(':')[0] == 'bitcoin'):
            receipentaddress = receipentaddress.split(':')[1].split('?')[0]
        if (receipentaddress[:3] == 'bc1') or (receipentaddress[:1] == '3') or (receipentaddress[:1] == '1'):
            if not (len(receipentaddress) >= 26) and (len(receipentaddress) <= 35):
                error = receipentaddress + ' is not a valid bitcoin address, address should have a length from 26 to 35 instead of ' + str(len(receipentaddress)) + '.'
        else: 
            error = receipentaddress + ' is not a valid bitcoin address, address should have started with bc1, 3 or 1 instead of ' + receipentaddress[:1] + ', or ' + receipentaddress[:3] + '.'
        if error:
            return redirect('/Recovery/step11')
        return redirect('/Recovery/step1215')
    return render_template('YWRstep11.html', error=error)

@app.route('/Recovery/step1215', methods=['GET', 'POST'])
def Recovery_step1215():
    global privkeylist
    global xprivlist
    global newxpublist
    global privkeycount
    global error 
    if request.method == 'POST':
        privkey = []
        for i in range(1,14):
            inputlist = request.form['row' + str(i)]
            inputlist = inputlist.split(' ')
            inputlist = inputlist[0:4]
            privkey.append(inputlist[0])
            privkey.append(inputlist[1])
            privkey.append(inputlist[2])
            privkey.append(inputlist[3])
        privkeylist.append(PassphraseListToWIF(privkey))
        error = None
        privkeycount = privkeycount + 1
        if (privkeycount >= 3):
            newxpublist = []
            for i in range(0,3):
                rpc = RPC()
                home = os.getenv('HOME')
                path = home + '/blank' + str(i)
                response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli createwallet "blank'+str(i)+'" false true'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                print(response)
                response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli loadwallet "blank'+str(i)+'"'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                print(response)
                response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli -rpcwallet=blank'+str(i)+' sethdseed false "'+privkeylist[i]+'"'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                print(response)
                if not (len(response[1]) == 0): 
                    print(response)
                    return "error response from sethdseed: " + str(response[1]) + '\n' + '~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli -rpcwallet=blank'+str(i)+' sethdseed false "'+privkeylist[i]+'"'
                response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli -rpcwallet=blank'+str(i)+' dumpwallet "blank'+str(i)+'"'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                print(response)
                wallet = open(path,'r')
                wallet.readline()
                wallet.readline()
                wallet.readline()
                wallet.readline()
                wallet.readline()
                privkeyline = wallet.readline()
                privkeyline = privkeyline.split(" ")[4][:-1]
                xprivlist.append(privkeyline)
                response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli getdescriptorinfo "pk('+privkeyline+')"'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                print(response)
                if not (len(response[0]) == 0): 
                    response = response[0].decode("utf-8")
                else:
                    print(response)
                    return "error response from getdescriptorinfo: " + str(response[1]) + '\n' + '~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli getdescriptorinfo "pk('+privkeyline+')"'
                xpub = response.split('(')[1].split(')')[0]
                newxpublist.append(xpub)
                privkeycount = 0
            return redirect('/Recovery/step16')
        else:
            return redirect('/Recovery/step1215')
    return render_template('YWRstep1215.html', x=privkeycount + 1, error=error,i=privkeycount + 26 )

#stop bitocin qt and delete wallet
@app.route("/Recovery/step16", methods=['GET', 'POST'])
def Recovery_step16():
    if request.method == 'POST':
        subprocess.call('gnome-terminal -- bash -c "sudo python3 ~/yeticold/utils/deleteallwallets.py; echo "DONE, Close this window.""', shell=True)
        return redirect('/Recovery/step17')
    return render_template('YWRstep16.html')

#reopen bitcoin
@app.route("/Recovery/step17", methods=['GET', 'POST'])
def Recovery_step17():
    if request.method == 'POST':
        subprocess.Popen('~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-qt -proxy=127.0.0.1:9050',shell=True,start_new_session=True)
        return redirect('/Recovery/step18')
    return render_template('YWRstep17.html')

#finish reopen bitcoin
@app.route('/Recovery/step18', methods=['GET', 'POST'])
def Recovery_step18():
    global progress
    if request.method == 'GET':
        progress = BTCprogress()
    if request.method == 'POST':
        if progress >= 99:
            return redirect('/Recovery/step19')
        else:
            return redirect('/Recovery/step18')
    return render_template('YCRstep18.html', progress=progress)

#GEN trans qr code
@app.route("/Recovery/step19", methods=['GET', 'POST'])
def Recovery_step19():
    global xprivlist
    global newxpublist
    global pubdesc
    global sourceaddress
    global receipentaddress
    global minerfee
    if request.method == 'GET':
        xpublist = pubdesc.decode("utf-8").split(',')[1:]
        xpublist[6] = xpublist[6].split('))')[0]
        descriptorlist = xpublist
        for i in range(0,3):
            xpub = newxpublist[i] + '/*'
            for x in range(0,7):
                oldxpub = xpublist[x]
                if xpub == oldxpub:
                    descriptorlist[x] = (xprivlist[i] + '/*')
                    break
        desc = '"wsh(multi(3,'+descriptorlist[0]+','+descriptorlist[1]+','+descriptorlist[2]+','+descriptorlist[3]+','+descriptorlist[4]+','+descriptorlist[5]+','+descriptorlist[6]+'))'
        response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli getdescriptorinfo '+desc+'"'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        print(response)
        if not (len(response[0]) == 0): 
            response = json.loads(response[0].decode("utf-8"))
        else:
            print(response)
            return "error response from getdescriptorinfo: " + str(response[1]) + '\n' + '~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli getdescriptorinfo '+desc+'"'
        checksum = response["checksum"]
        response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli importmulti \'[{ "desc": '+desc+'#'+ checksum +'", "timestamp": "now", "range": [0,999], "watchonly": false, "label": "test" }]\' \'{"rescan": true}\''],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        print(response)
        if not (len(response[1]) == 0): 
            print(response)
            return "error response from importmulti: " + str(response[1]) + '\n' + '~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli importmulti \'[{ "desc": '+desc+'#'+ checksum +'", "timestamp": "now", "range": [0,999], "watchonly": false, "label": "test" }]\' \'{"rescan": true}\''
        rpc = RPC()
        minerfee = float(rpc.estimatesmartfee(6)["feerate"])
        kilobytespertrans = 0.200
        minerfee = (minerfee * kilobytespertrans)
        amo = (sourceaddress['numbal'] - minerfee)
        amo = "{:.8f}".format(float(amo))
        response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli createrawtransaction \'[{ "txid": "'+sourceaddress['txid']+'", "vout": '+sourceaddress['vout']+'}]\' \'[{"'+receipentaddress+'" : '+str(amo)+'}]\''],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        print(response)
        if not (len(response[0]) == 0): 
            response = response[0].decode("utf-8")
        else:
            print(response)
            return "error response from createrawtransaction: " + str(response[1]) + '\n' + '~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli createrawtransaction \'[{ "txid": "'+sourceaddress['txid']+'", "vout": '+sourceaddress['vout']+'}]\' \'[{"'+receipentaddress+'" : '+str(amo)+'}]\''
        transonehex = response[:-1]
        response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli signrawtransactionwithwallet '+transonehex],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        print(response)
        if not (len(response[0]) == 0): 
            response = json.loads(response[0].decode("utf-8"))
        else:
            print(response)
            return "error response from signrawtransactionwithwallet: " + str(response[1]) + '\n' + '~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli signrawtransactionwithwallet '+transonehex
        transone = response
    if request.method == 'POST':
        response = subprocess.Popen(['~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli sendrawtransaction '+transone+''],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        print(response)
        if not (len(response[1]) == 0): 
            return "error response from sendrawtransaction: " + response[1] + '\n' + '~/yeticold/bitcoin-0.19.0rc1/bin/bitcoin-cli sendrawtransaction '+transone+''
        return redirect('/menu')
    return render_template('YWRstep19.html', amount=amo, minerfee=minerfee, recipent=receipentaddress)






### END OF ONLINE

@app.route("/step")
def step():
    return "This page has not been added yet"

if __name__ == "__main__":
    app.run()