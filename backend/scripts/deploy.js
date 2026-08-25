import hre from "hardhat";

async function main() {
  console.log("🚀 Deploying EvidenceRegistry smart contract from ./blockchain_layer ...");

  // Hardhat automatically finds EvidenceRegistry because of our paths config
  const EvidenceRegistry = await hre.ethers.getContractFactory("EvidenceRegistry");
  const registry = await EvidenceRegistry.deploy();

  await registry.waitForDeployment();

  const contractAddress = await registry.getAddress();
  console.log(`\n✨ Smart Contract Successfully Deployed!`);
  console.log(`📍 Contract Address: ${contractAddress}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});