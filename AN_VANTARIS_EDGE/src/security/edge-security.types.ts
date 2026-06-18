export interface PayloadHashDescriptor {
  hashAlgorithm: string;
  payloadHash: string;
}

export interface SignaturePayloadDescriptor {
  signatureAlgorithm: string;
  signature?: string;
  signedAt?: string;
  /* transitionOnly: true */
}
