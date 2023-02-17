const plagiarism=artifacts.require('plagiarism');

module.exports=function(deployer){
    deployer.deploy(plagiarism);
}