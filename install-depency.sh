#! /bin/bash

#========================================================================
#                            install JDK、Maven、node、 by yum
#
#                            author: wyl
#========================================================================

hasJdk(){
    java -version
    if [ $? -eq 0 ]; then
      return 1;
    else
      return 0;
    fi
}

hasMaven(){
    MAVEN_VERSION=$(mvn -version)
    echo "${MAVEN_VERSION}"
    if [[ ! $MAVEN_VERSION ]]
    then
        return 0;
    fi
    return 1;
}


hasNode(){
    NODE_RESULT=$(node -v)
    echo "${NODE_RESULT}"
    if [[ ! $NODE_RESULT ]]
    then
        return 0;
    fi
    return 1;
}

isArm64(){
  get_arch=`arch`
  if [[ $get_arch =~ "x86_64" ]];then
      return 0
  elif [[ $get_arch =~ "aarch64" ]];then
      return 1
  elif [[ $get_arch =~ "mips64" ]];then
      return 0
  else
      return 0
  fi
}
isOpenEuler(){
  OS_NAME=$(uname -a)
  OL_MARK="oe1"
  if [[ $OS_NAME =~ $OL_MARK ]]
  then
    return 1
  else
    return 0
  fi
}

yum install -y tar
hasJdk
if [ $? != 1 ]
then
    echo "Not Found jdk"
    echo "Installing jdk..."
    isArm64
    if [ $? != 1 ]
    then
      wget https://mirrors.huaweicloud.com/kunpeng/archive/compiler/bisheng_jdk/bisheng-jdk-11.0.17-linux-x64.tar.gz
      tar zxvf bisheng-jdk-11.0.17-linux-x64.tar.gz -C /etc/
      mv /etc/bisheng-jdk-11.0.17 /etc/jdk11
      rm -rf bisheng-jdk-11.0.17-linux-x64.tar.gz
    else
      wget https://mirrors.huaweicloud.com/kunpeng/archive/compiler/bisheng_jdk/bisheng-jdk-11.0.17-linux-aarch64.tar.gz
      tar zxvf bisheng-jdk-11.0.17-linux-aarch64.tar.gz -C /etc/
      mv /etc/bisheng-jdk-11.0.17 /etc/jdk11
      rm -rf bisheng-jdk-11.0.17-linux-aarch64.tar.gz
    fi
    hasJdk
    if [ $? != 1 ]
    then
      echo "Install jdk Fail"
    fi
fi


hasMaven
if [ $? != 1 ]
then
    echo "Not Found maven"
    echo "Installing maven..."

    wget --no-check-certificate  https://mirrors.tuna.tsinghua.edu.cn/apache/maven/maven-3/3.9.3/binaries/apache-maven-3.9.3-bin.tar.gz

    tar -zxvf apache-maven-3.9.3-bin.tar.gz -C /etc/
    sed -i '30 i JAVA_HOME=/etc/jdk11' /etc/apache-maven-3.9.3/bin/mvn
    if [ ! -f "/usr/local/bin/mvn" ]; then
      ln -s /etc/apache-maven-3.9.3/bin/mvn /usr/local/bin/mvn
    fi

    hasMaven
    if [ $? == 1 ]
    then
      echo "Config Aliyun Maven Mirror..."
      rm -rf /etc/apache-maven-3.9.3/conf/settings.xml
      cp config/settings.xml /etc/apache-maven-3.9.3/conf/
      mvn -version

      rm -rf apache-maven-3.9.3-bin.tar.gz
    else
      echo "Install maven Fail"
    fi
fi
echo ""


hasNode
if [ $? != 1 ]
then
    echo "Not Found nodejs"
    echo "Installing nodejs..."

    isArm64
    if [ $? != 1 ]
    then
      wget https://nodejs.org/dist/v16.15.1/node-v16.15.1-linux-x64.tar.xz
      tar -xvf node-v16.15.1-linux-x64.tar.xz -C /etc/

      if [ ! -f "/usr/bin/node" ]; then
        ln -s /etc/node-v16.15.1-linux-x64/bin/node /usr/bin/node
      fi

      if [ ! -f "/usr/bin/npm" ]; then
        ln -s /etc/node-v16.15.1-linux-x64/bin/npm /usr/bin/npm
      fi

      if [ ! -f "/usr/local/bin/node" ]; then
        ln -s /etc/node-v16.15.1-linux-x64/bin/node /usr/local/bin/node
      fi

      if [ ! -f "/usr/local/bin/npm" ]; then
        ln -s /etc/node-v16.15.1-linux-x64/bin/npm /usr/local/bin/npm
      fi
      rm -rf node-v16.15.1-linux-x64.tar.xz
    else
      wget https://nodejs.org/dist/v16.15.1/node-v16.15.1-linux-arm64.tar.gz
      tar -xvf node-v16.15.1-linux-arm64.tar.gz -C /etc/

      if [ ! -f "/usr/bin/node" ]; then
        ln -s /etc/node-v16.15.1-linux-arm64/bin/node /usr/bin/node
      fi

      if [ ! -f "/usr/bin/npm" ]; then
        ln -s /etc/node-v16.15.1-linux-arm64/bin/npm /usr/bin/npm
      fi

      if [ ! -f "/usr/local/bin/node" ]; then
        ln -s /etc/node-v16.15.1-linux-arm64/bin/node /usr/local/bin/node
      fi

      if [ ! -f "/usr/local/bin/npm" ]; then
        ln -s /etc/node-v16.15.1-linux-arm64/bin/npm /usr/local/bin/npm
      fi
      rm -rf node-v16.15.1-linux-arm64.tar.gz
    fi
    npm config set registry http://registry.npmmirror.com/
    hasNode
    if [ $? != 1 ]
    then
      echo "Install nodejs Fail"
    fi
fi
