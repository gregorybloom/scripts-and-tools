timestamp() {
  date +"%Y-%m-%d_%H-%M-%S"
}


currtime=$(timestamp)
echo "time: $currtime"
echo ""


source "config/findsshkeypath.sh"
source "config/grab_server100_info.sh"
source "config/grab_server111_info.sh"

APPNAME="nodepython"
APPPATH="/$APPNAME"
RETRIEVEPATH="../../retrieve"

rm -rf "$RETRIEVEPATH"

lsRemote()
{
  ssh -T -i "$sshkey" -o PreferredAuthentications=publickey -p "$_SERVER100_PORT" "$_SERVER100_USER@$_SERVER100_IP" <<EOF
  	ls -l "$1"
EOF
}
rmRemote()
{
  ssh -i "$sshkey" -o PreferredAuthentications=publickey -p "$_SERVER100_PORT" "$_SERVER100_USER@$_SERVER100_IP" <<EOF
    rm -rf "$1"
EOF
}
isDirInLsRemote()
{
  resultsC=$(lsRemote "$1")
  sfolders=()
  searchResults "${resultsC[@]}" "sfolders" 1
  for line in "${sfolders[@]}"; do
    if [[ "$line" == "$2" ]]; then
      return 0
    fi
  done
  return 1
}
searchResults()
{
  resultL="$1"
  list="$2"
  rtype="$3"
  for txt in "${resultL[@]}"; do
    while IFS= read -r line; do
      test_str="$line"

      regexa=".*"
      regexb=".*"
      if [ "$rtype" -eq "1" ]; then
        regexa="^d[rwx\-]{9}[ ]+[0-9]+[ ]+[A-Za-z_]+[ ]+[A-Za-z_]+[ ]+[0-9]+[ ]+[A-Za-z_0-9 ]+\:[0-9]+[ ]+([A-Za-z0-9_]+)"
        regexb="^d[rwx\-]{9}[ ]+[0-9]+[ ]+[A-Za-z_]+[ ]+[A-Za-z_]+[ ]+[0-9]+[ ]+[A-Za-z]+[ ]+[0-9]+[ ]+[0-9]+[ ]+([A-Za-z0-9_]+)"
      elif [ "$rtype" -eq "2" ]; then
        regexa="^.[rwx\-]{9}[ ]+[0-9]+[ ]+[A-Za-z_]+[ ]+[A-Za-z_]+[ ]+[0-9]+[ ]+[A-Za-z_0-9 ]+\:[0-9]+[ ]+(lock_[A-Za-z0-9_\.]+\.txt)"
        regexb="^.[rwx\-]{9}[ ]+[0-9]+[ ]+[A-Za-z_]+[ ]+[A-Za-z_]+[ ]+[0-9]+[ ]+[A-Za-z]+[ ]+[0-9]+[ ]+[0-9]+[ ]+(lock_[A-Za-z0-9_\.]+\.txt)"
      fi
      if [[ $test_str =~ $regexa ]]; then
          name="${BASH_REMATCH[1]}"
          eval "$list+=($(printf "'%s' " "${name}"))"
      elif [[ $test_str =~ $regexb ]]; then
          name="${BASH_REMATCH[1]}"
          eval "$list+=($(printf "'%s' " "${name}"))"
      fi
    done< <(printf '%s\n' "$txt")
  done
}
pushTo111Server()
{
  lpath="$1"
  if nc -z "$_SERVER111_IP" "$_SERVER111_PORT" 2>/dev/null; then
    rm -rf "$RETRIEVEPATH"
    mkdir -p "$RETRIEVEPATH"
    chmod 755 -R "$RETRIEVEPATH"

    pathfolders=("pythondl" "pythonlog" "pythonmsgs")
    for npath in "${pathfolders[@]}"; do
      if [ ! -d "$RETRIEVEPATH/$npath" ]; then
        mv "$lpath/$npath" "$RETRIEVEPATH"
      fi
    done

    num=$(find "$RETRIEVEPATH/" -maxdepth 1 -type d | wc -l)
    if [ "$num" -gt "1" ]; then
      rsync --no-links -e "ssh -p $_SERVER111_PORT" -avvzcWP --port="$_SERVER111_PORT" "$RETRIEVEPATH/" "$_SERVER111_USER@$_SERVER111_IP:$_PYTHONDUMP_PATH"
      if [ "$?" -eq "0" ]; then
        rm -rf "$RETRIEVEPATH/"
        echo "Done SERVER copy"
      else
        echo "Error while running rsync"
      fi
    fi

  else
      echo "SERVER not accessible"
  fi
}




pushTo111Server "$_LOCALBACKUP_PATH"



results=$(lsRemote "/$_SERVER100_WEBPATH/$APPPATH/pythonbranches")
sfolders=()
searchResults "${results[@]}" "sfolders" 1
sourcefolders=("")
for spath in "${sfolders[@]}"; do
  sourcefolders+=("pythonbranches/${spath}/")
done


mkdir -p "$RETRIEVEPATH"
chmod 755 -R "$RETRIEVEPATH"

pathfolders=("pythondl" "pythonlog" "pythonmsgs")
for spath in "${sourcefolders[@]}"; do
  downloadLock=0
  for path in "${pathfolders[@]}"; do
    if [ "$downloadLock" -eq "1" ]; then
      continue
    fi

		mkdir -p "$RETRIEVEPATH/ret_tmp"

    fpath="$_SERVER100_WEBPATH/$APPPATH/$spath$path"
    echo "-- $fpath"
    if isDirInLsRemote "$_SERVER100_WEBPATH/$APPPATH/$spath" "$path"; then
      echo ""
    else
      continue
    fi

    if [[ "$path" == "pythondl" ]]; then
      results2=$(lsRemote "$fpath")
      branchlist=()
      searchResults "${results2[@]}" "branchlist" 1

      locklist=()
      for brname in "${branchlist[@]}"; do
        resultsBR=$(lsRemote "$fpath/$brname")
        searchResults "${resultsBR[@]}" "locklist" 2
      done
      if [ ${#locklist[@]} -ne 0 ]; then
        downloadLock=1
      fi
      if [ "$downloadLock" -eq "1" ]; then
        echo "LOCKED: $spath"
        continue
      fi

    fi
		rsync --exclude-from '../r_excludes.txt' --temp-dir='ret_tmp' -e "ssh -i $sshkey -o PreferredAuthentications=publickey -p $_SERVER100_PORT" -avvzcWP --port="$_SERVER100_PORT" "$_SERVER100_USER@$_SERVER100_IP:$fpath" "$RETRIEVEPATH"
		rm -rf "$RETRIEVEPATH/ret_tmp"

		rsync -a "$RETRIEVEPATH/" "$_LOCALBACKUP_PATH"
		chmod 755 -R "$_LOCALBACKUP_PATH"

    if [[ "$path" == "pythondl" ]]; then
      fpath="$_SERVER100_WEBPATH/$APPPATH/$spath$path"
      results=$(rmRemote "$fpath")
    fi
	done
done
rm -rf "$RETRIEVEPATH/"

pushTo111Server "$_LOCALBACKUP_PATH"
