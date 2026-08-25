// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract EvidenceRegistry {
    struct Evidence {
        string videoUrl;
        string reportUrl;
        uint256 confidenceScore;
        uint256 timestamp;
        address investigator;
        bool isVerified;
    }

    mapping(bytes32 => Evidence) public registry;

    function logEvidence(
        bytes32 _fileHash,
        string memory _videoUrl,
        string memory _reportUrl,
        uint256 _confidenceScore
    ) public {
        registry[_fileHash] = Evidence({
            videoUrl: _videoUrl,
            reportUrl: _reportUrl,
            confidenceScore: _confidenceScore,
            timestamp: block.timestamp,
            investigator: msg.sender,
            isVerified: true
        });
    }
}
