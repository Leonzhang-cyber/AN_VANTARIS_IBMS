// src/blockchain/contracts/IMBSAnchor.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract IMBSAnchor {
    // 实体锚定：did => 元数据哈希
    mapping(string => string) public entityMetadataHash;
    // VC 锚定：vcId => VC 哈希
    mapping(string => string) public vcHash;
    // VC 撤销状态：vcId => 是否已撤销
    mapping(string => bool) public vcRevoked;

    // 事件：实体注册锚定
    event EntityAnchored(
        string indexed did,
        string metadataHash,
        address indexed operator,
        uint256 timestamp
    );

    // 事件：VC 签发锚定
    event VCIssuedAnchored(
        string indexed vcId,
        string vcHash,
        string indexed issuerDid,
        string indexed subjectDid,
        uint256 timestamp
    );

    // 事件：VC 撤销
    event VCRevoked(
        string indexed vcId,
        address indexed operator,
        uint256 timestamp
    );

    // 锚定实体元数据哈希（注册新实体时调用）
    function anchorEntity(string memory did, string memory metadataHash) public {
        require(bytes(entityMetadataHash[did]).length == 0, "Entity already anchored");
        entityMetadataHash[did] = metadataHash;
        emit EntityAnchored(did, metadataHash, msg.sender, block.timestamp);
    }

    // 更新实体元数据哈希（信息变更时调用）
    function updateEntity(string memory did, string memory newMetadataHash) public {
        require(bytes(entityMetadataHash[did]).length != 0, "Entity not found");
        entityMetadataHash[did] = newMetadataHash;
        emit EntityAnchored(did, newMetadataHash, msg.sender, block.timestamp);
    }

    // 锚定 VC 哈希（签发 VC 时调用）
    function anchorVC(
        string memory vcId,
        string memory _vcHash,
        string memory issuerDid,
        string memory subjectDid
    ) public {
        require(bytes(vcHash[vcId]).length == 0, "VC already anchored");
        vcHash[vcId] = _vcHash;
        emit VCIssuedAnchored(vcId, _vcHash, issuerDid, subjectDid, block.timestamp);
    }

    // 撤销 VC
    function revokeVC(string memory vcId) public {
        require(!vcRevoked[vcId], "VC already revoked");
        vcRevoked[vcId] = true;
        emit VCRevoked(vcId, msg.sender, block.timestamp);
    }

    // 查询实体哈希
    function getEntityHash(string memory did) public view returns (string memory) {
        return entityMetadataHash[did];
    }

    // 查询 VC 哈希
    function getVCHash(string memory vcId) public view returns (string memory) {
        return vcHash[vcId];
    }

    // 检查 VC 是否被撤销
    function isVCRevoked(string memory vcId) public view returns (bool) {
        return vcRevoked[vcId];
    }
}