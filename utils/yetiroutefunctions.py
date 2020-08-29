from imports import *
import variables as v
from yetifunctions import *
from btcrpcfunctions import *
home = os.getenv("HOME")



def blockChain(request, nextroute):
    if request.method == 'GET':
        if (os.path.exists(home + "/.bitcoin")):
            createOrPrepend('\nserver=1\nrpcport=8332\nrpcuser=rpcuser\nrpcpassword='+v.rpcpsw+'\n',home+'/.bitcoin/bitcoin.conf')
            return redirect(nextroute)
    if request.method == 'POST':
        if request.form['option'] == 'downloadblockchain':
            subprocess.call('python3 ~/yeticold/utils/testblockchain.py',shell=True)
        else:
            subprocess.call('mkdir ~/.bitcoin',shell=True)
            if request.form['date'] == '':
                createOrPrepend('\nserver=1\nrpcport=8332\nrpcuser=rpcuser\nrpcpassword='+v.rpcpsw+'\n',home+'/.bitcoin/bitcoin.conf')
                return redirect(nextroute)
            createOrPrepend('server=1\nrpcport=8332\nrpcuser=rpcuser\nprune='+str(getPrunBlockheightByDate(request))+'\nrpcpassword='+v.rpcpsw+'',home+'/.bitcoin/bitcoin.conf')
        return redirect(nextroute)

def openBitcoin(request, currentroute, nextroute):
    if request.method == 'GET':
        if (os.path.exists(home + "/.bitcoin")):
            testblockchain = False
        if BTCClosed():
            if testblockchain == False:
                subprocess.Popen('~/yeticold/bitcoin/bin/bitcoin-qt -proxy=127.0.0.1:9050',shell=True,start_new_session=True)
        v.IBD = BTCFinished()
        v.progress = BTCprogress()
    if request.method == 'POST':
        if v.IBD:
            subprocess.call(['~/yeticold/bitcoin/bin/bitcoin-cli createwallet "yetiwarm"'],shell=True)
            return redirect(nextroute)
        else:
            return redirect(currentroute)

def getSeeds(request, nextroute):
    if request.method == 'POST':
        if request.form['skip'] == 'skip':
            v.privkeylist = generatePrivKeys('1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111')
        else:
            v.privkeylist = generatePrivKeys(request.form['binary' + str(i)])
        for i in range(0,7):
            handleResponse('~/yeticold/bitcoin/bin/bitcoin-cli createwallet "yetiwalletone'+str(i)+'"')
            handleResponse('~/yeticold/bitcoin/bin/bitcoin-cli -rpcwallet=yetiwalletone'+str(i)+' sethdseed true "'+v.privkeylist[i]+'"')
            handleResponse('~/yeticold/bitcoin/bin/bitcoin-cli -rpcwallet=yetiwalletone'+str(i)+' dumpwallet "yetiwalletone'+str(i)+'"')
            xpriv = getxpriv(home + '/yetiwalletone' + str(i))
            xprivlist.append(xpriv)
        v.addresses = []
        checksum = None
        response = handleResponse('~/yeticold/bitcoin/bin/bitcoin-cli -rpcwallet=yetiwallet getdescriptorinfo "wsh(multi(3,'+v.xprivlist[0]+'/*,'+v.xprivlist[1]+'/*,'+v.xprivlist[2]+'/*,'+v.xprivlist[3]+'/*,'+v.xprivlist[4]+'/*,'+v.xprivlist[5]+'/*,'+v.xprivlist[6]+'/*))"', True)
        checksum = response["checksum"]
        v.pubdesc = response["descriptor"].replace('\n', '')
        handleResponse('~/yeticold/bitcoin/bin/bitcoin-cli -rpcwallet=yetiwallet importmulti \'[{ "desc": "'+pubdesc+'", "timestamp": "now", "range": [0,999], "watchonly": false}]\' \'{"rescan": true}\'')
        handleResponse('~/yeticold/bitcoin/bin/bitcoin-cli createwallet "yetiwalletpriv"')
        handleResponse('~/yeticold/bitcoin/bin/bitcoin-cli -rpcwallet=yetiwalletpriv importmulti \'[{ "desc": "wsh(multi(3,'+v.xprivlist[0]+'/*,'+v.xprivlist[1]+'/*,'+v.xprivlist[2]+'/*,'+v.xprivlist[3]+'/*,'+v.xprivlist[4]+'/*,'+v.xprivlist[5]+'/*,'+v.xprivlist[6]+'/*))#'+checksum+'", "timestamp": "now", "range": [0,999], "watchonly": false}]\' \'{"rescan": true}\'')
        v.walletimported = True
        path = home + '/Documents'
        subprocess.call('rm -r '+path+'/yetiseed*', shell=True)
        return redirect(nextroute)

def displaySeeds(request, currentroute, nextroute):
    if request.method == 'GET':
        privkey = v.privkeylist[v.privkeycount]
        passphraselist = ConvertToPassphrase(privkey)
    if request.method == 'POST':
        path = home + '/Documents'
        subprocess.call('mkdir '+path+'/yetiseed'+str(v.privkeycount + 1), shell=True)
        subprocess.call('touch '+path+'/yetiseed'+str(v.privkeycount + 1)+'/yetiseed'+str(v.privkeycount + 1)+'.txt', shell=True)
        file = ''
        for i in range(0,13):
            file = file + request.form['displayrow' + str(i+1)] + '\n'
        file = file + '\n\nThis is your descriptor in text format you have a duplicate of this text in QR format in this folder.\n' + pubdesc + '\n'
        file = file + '\n\nThis is a seed packet that contains 1/3 of the information needed to recover bitcoins in a 3 of 7 HD multisig wallet.\n'
        file = file + 'There are 6 other packets that are identical except that they contain one of the other sets of seed words.\n'
        file = file + 'The HD Multisig wallet was was created using YetiCold.com (a Python script to make the experience more user friendly) and Bitcoin Core 0.19 RC1.\n'
        file = file + 'To recover the bitcoin go to YetiCold.com click your version of yeti and follow the instructions.\n'
        file = file + 'YetiCold.com should direct you to download a script to make the process of using Bitcoin Core easier, but never trust any website with your seed words.\n'
        file = file + 'Consider putting a small amount of money into YetiCold.com cold storage and recovering them before attempting to recover significant funds.\n'
        file = file + 'A test run will give you the opportunity to make sure that your seed words are never connected to an online device before.\n'
        file = file + 'If many years have passed you should check that YetiCold.com has retained a good reputation.\n'
        file = file + 'If YetiCold.com is no longer reputable use Bitcoin Core alone to recover your bitcoin (with the help of a trusted expert only if absolutely needed as these people may attempt to steal the bitcoin).\n'
        file = file + 'No software beyond Bitcoin Core is required to recover the stored bitcoin.\n'
        file = file + 'This seed packet also contains a usb device that has a digital copy of the information on this document. It does not contain another set of seed words, but simply a copy of the seed words in this document.\n'
        file = file + 'Two other seed packets must be obtained to recover the bitcoin stored.\n'
        file = file + 'YetiCold.com recommends storing seed words in locations like safety deposit boxes, home safes, and with professionals such as accountants and lawyers.\n'
        createOrPrepend(file, path+'/yetiseed'+str(v.privkeycount + 1)+'/yetiseed'+str(v.privkeycount + 1)+'.txt')
        makeQrCode(v.pubdesc, home+'/Documents/yetiseed'+str(v.privkeycount+1)+'/descriptor.png')
        v.privkeycount = v.privkeycount + 1
        if (v.privkeycount == 7):
            v.privkeycount = 0
            return redirect(nextroute)
        else:
            return redirect(currentroute)

def checkSeeds(request, currentroute, nextroute):
    if request.method == 'POST':
        privkey = v.privkeylist[v.privkeycount]
        passphraselist = ConvertToPassphrase(privkey)
        privkeylisttoconfirm = []
        v.oldkeys = []
        for i in range(1,14):
            inputlist = request.form['row' + str(i)]
            v.oldkeys.append(inputlist)
            inputlist = inputlist.split(' ')
            inputlist = inputlist[0:4]
            privkeylisttoconfirm.append(inputlist[0])
            privkeylisttoconfirm.append(inputlist[1])
            privkeylisttoconfirm.append(inputlist[2])
            privkeylisttoconfirm.append(inputlist[3])
        if privkeylisttoconfirm == passphraselist:
            v.oldkeys = None
            v.error = None
            v.privkeycount = v.privkeycount + 1
            if (v.privkeycount >= 7):
                v.privkeycount = 7
                v.newxprivlist = []
                for i in range(0,7):
                    handleResponse('~/yeticold/bitcoin/bin/bitcoin-cli createwallet "yetiwallettwo"'+str(i)+'"')
                    handleResponse('~/yeticold/bitcoin/bin/bitcoin-cli -rpcwallet=yetiwallettwo'+str(i)+' sethdseed true "'+v.privkeylist[i]+'"')
                    handleResponse('~/yeticold/bitcoin/bin/bitcoin-cli -rpcwallet=yetiwallettwo'+str(i)+' dumpwallet "yetiwallettwo'+str(i)+'"')
                    xpriv = getxpriv(home + '/yetiwallettwo' + str(i))
                    v.newxprivlist.append(xpriv)
                    if not v.xprivlist[i] == v.newxprivlist[i]:
                        v.privkeycount = 0
                        v.privkeylist = []
                        v.error = 'You have imported your seeds correctly but your xprivs do not match: This means that you either do not have bitcoin running or its initial block download mode. Another issue is that you have a wallet folder or wallet dump file that was not deleted before starting this step.'
                        return redirect(currentroute)
                return redirect(nextroute)
            else:
                return redirect(currentroute)
        else:
            v.error = 'The seed words you entered are incorrect. This is probably because you entered a line twice or put them in the wrong order.'

def importSeeds(request, currentroute, nextroute):
    if request.method == 'GET':
        if v.walletimported:
            return redirect('/YWRsendtransactionB')
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
        v.privkeylist.append(PassphraseToWIF(privkey))
        error = None
        v.privkeycount = v.privkeycount + 1
        if (v.privkeycount >= 3):
            (v.xprivlist, v.newxpublist) = getxprivs(v.privkeylist)
            v.privkeycount = 0
            xpublist = pubdesc.split(',')[1:]
            xpublist[6] = xpublist[6].split('))')[0]
            descriptorlist = xpublist
            for i in range(0,3):
                xpub = v.newxpublist[i] + '/*'
                for x in range(0,7):
                    oldxpub = xpublist[x]
                    if xpub == oldxpub:
                        descriptorlist[x] = (v.xprivlist[i] + '/*')
                        break
            desc = '"wsh(multi(3,'+descriptorlist[0]+','+descriptorlist[1]+','+descriptorlist[2]+','+descriptorlist[3]+','+descriptorlist[4]+','+descriptorlist[5]+','+descriptorlist[6]+'))'
            print(desc)
            handleResponse('~/yeticold/bitcoin/bin/bitcoin-cli createwallet "yetiwarmpriv"')
            response = handleResponse('~/yeticold/bitcoin/bin/bitcoin-cli -rpcwallet=yetiwarmpriv getdescriptorinfo '+desc+'"', True)
            checksum = response["checksum"]
            handleResponse('~/yeticold/bitcoin/bin/bitcoin-cli -rpcwallet=yetiwarmpriv importmulti \'[{ "desc": '+desc+'#'+ checksum +'", "timestamp": "now", "range": [0,999], "watchonly": false}]\' \'{"rescan": true}\'')
            v.walletimported = True
            return redirect('/YWRsendtransaction')
        else:
            return redirect('/YWRimportseeds')

def sendTransactions(request, currentroute, nextroute):
    if request.method == 'GET':
        rpc = RPC("yetiwallet")
        v.minerfee = float(rpc.estimatesmartfee(1)["feerate"])
        kilobytespertrans = 0.200
        v.minerfee = (v.minerfee * kilobytespertrans)
        v.amo = (float(v.sourceaddress['numbal']) - v.minerfee)
        v.amo = "{:.8f}".format(float(v.amo))
        if v.amo <= 0:
            v.error = "Amount is too small to account for the fee. Try sending a larger amount."
            return redirect(currentroute)
        response = handleResponse('~/yeticold/bitcoin/bin/bitcoin-cli -rpcwallet=yetiwarmpriv createrawtransaction \'[{ "txid": "'+v.sourceaddress['txid']+'", "vout": '+str(sourceaddress['vout'])+'}]\' \'[{"'+v.receipentaddress+'" : '+str(v.amo)+'}]\'')
        transonehex = response[:-1]
        response = handleResponse('~/yeticold/bitcoin/bin/bitcoin-cli -rpcwallet=yetiwarmpriv signrawtransactionwithwallet '+transonehex, True)
        if not response['complete']:
            raise werkzeug.exceptions.InternalServerError(response['errors'][0]['error'])
        transnum = response
        v.minerfee = "{:.8f}".format(v.minerfee)
    if request.method == 'POST':
        handleResponse('~/yeticold/bitcoin/bin/bitcoin-cli -rpcwallet=yetiwarmpriv sendrawtransaction '+transnum['hex']+'')
        return redirect(nextroute)
