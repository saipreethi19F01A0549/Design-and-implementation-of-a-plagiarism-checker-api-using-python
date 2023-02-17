// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract plagiarism {
  
  address[] _usernames;
  string[] _hashes;

  mapping (string=>bool) _documents;

  function adddocument(address username, string memory _hash) public {
    require (!_documents[_hash]);

    _documents[_hash]=true;
    _usernames.push(username);
    _hashes.push(_hash);
  }

  function viewdocuments() public view returns(address[] memory, string[] memory){
    return(_usernames,_hashes);
  }

}
