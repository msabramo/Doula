rm -rf $VIRTUAL_ENV/build
ZMQVERSION=zeromq-2.1.11
if [ ! -d $ZMQVERSION ]
then
    wget -O - "http://download.zeromq.org/${ZMQVERSION}.tar.gz" | tar -xvzf -    
fi

pushd . > /dev/null
cd $ZMQVERSION
./configure --prefix $VIRTUAL_ENV
make; make install
ZMQ_DIR=$VIRTUAL_ENV pip install pyzmq
popd > /dev/null
mkdir $VIRTUAL_ENV/src
cd $VIRTUAL_ENV/src
git clone git@github.com:whitmo/gevent-zeromq.git
pip install distribute==0.6.14
#python setup.py build_ext --inplace -I$VIRTUAL_ENV/include
pushd .
cd gevent-zeromq
pip install -e ./
popd
pushd .
cd src
echo "<< Installing Doula and Bambino >>"
if [ ! -d ./Doula ]
then
    git clone git@github.com:SurveyMonkey/Doula.git
fi
pip install -r Doula/develop.txt
pip install -e ./Doula
if [ ! -d ./Doula ]
then
    git clone git@github.com:SurveyMonkey/Bambino.git
fi
pip install -r Bambino/develop.txt
pip install -e ./Bambino
popd
rm -rf $VIRTUAL_ENV/build