#!/bin/bash

printf "please input the file: user1.txt"
read filename
echo "continue(y/n)"
yn=(y/n)
    if test "yn" = "y" 
    then 
{ printf "please input the file: user2.txt"
read filename
echo "continue(y/n)
if test "yn" = "y"
    then
    { printf "please input the file: user3.txt"
        read filename
            if test "yn" = "y"
                then echo "continue"
            else
                echo "you can not input"
                fi
                exit 0
    }
else 
    echo "you can not iput"
          fi
              exit 0
}
else
echo "you can not input"
fi
exit 0
}
else exit 0
fi

    

function is_user_exist()
{
    {
    echo "begin funtion:"
        echo "pid: $$"

        all_names=`cat /etc/passwd|awk -F: '{print $1}'`
        for name in $all_names
            do
                if test $name = ${all_names[*]}
                    then
                        return 0
                else 
                    return 1
                        fi
                        done 

}
{ 
    echo "begin add_user"
username=`cat /etc/passwd |awk -F: '{print $1}'`
for v in $username
if $v = ${username[*]}
then
echo "username is exist"
else
useadd -m -d /home/$name -s /bin/bash $name
fi
exit 0
}
{
    echo "begin is_group_exist"
echo "pid: $$"
gname=`cat /etc/passwd |awk -F: '{print $1}'`
for v in $gname
do
if test $v = ${gname[*]}
then
return 0
else
return 1
    fi
    exit 0
}

{
echo "begin add_group" 

if is_group_exist  $1;
then
echo "group: $1 exist"
else
gruopadd $1
fi
}
{
echo "begin add_user_group:"
if is_user_exist $1 -a is_group_exist $1
then
echo "user $user is exist"
echo "group $group is exist"
else
  exec add_user && exec add_group 
      fi
      exit 0
}
}

