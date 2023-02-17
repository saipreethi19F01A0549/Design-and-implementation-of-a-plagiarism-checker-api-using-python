// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract register {

  address[] _usernames;
  uint[] _passwords;
  string[] _names;
  string[] _emails;

  mapping(address=>bool) users;

  function registeruser(address username, uint password, string memory name, string memory email) public{

    require(!users[username]);
    users[username]=true;

    _usernames.push(username);
    _passwords.push(password);
    _names.push(name);
    _emails.push(email);
  }

  function viewusers() public view returns(address[] memory,uint[] memory, string[] memory , string[] memory){
    return(_usernames,_passwords,_names,_emails);
  }

  function loginuser(address username,uint password) public view returns (bool){
    uint i;
    require(users[username]);

    for (i=0;i<_usernames.length;i++){
      if(_usernames[i]==username && _passwords[i]==password){
        return true;
      }
    }
    return false;
  }
}

