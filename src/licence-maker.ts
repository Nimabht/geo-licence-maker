import * as fs from "fs";
import * as crypto from "crypto";

interface License {
  customerId: string;
  startDate: string;
  endDate: string;
  modules: string[];
}

function generateLicense(
  customerId: string,
  modules: string[],
  startDate: string,
  endDate: string,
): string {
  const license: License = {
    customerId,
    startDate,
    endDate,
    modules,
  };

  const licenseData = JSON.stringify(license);

  const privateKey = fs.readFileSync("private_key.pem", "utf8");
  const sign = crypto.createSign("SHA256");
  sign.update(licenseData);
  const signature = sign.sign(privateKey, "hex");

  // Generate a random 129 character string
  const randomString = crypto.randomBytes(65).toString("hex"); // 65 bytes = 130 hex chars, but we need 129
  const random129Chars = randomString.substring(0, 129);

  const licenseWithSignature = {
    ...license,
    signature: `${random129Chars}${signature}`,
  };

  return JSON.stringify(licenseWithSignature);
}

function saveLicenseToFile(license: string, filename: string) {
  fs.writeFileSync(filename, license);
}

const customerId = "dev";
const modules = [
  "auth",
  "admin",
  "personal-space",
  "gps",
  "stations",
  "subscription",
  "ticket",
  "user",
  "ppk",
  "spp",
];
const startDate = "2025-06-01";
const endDate = "2025-09-31";

const license = generateLicense(customerId, modules, startDate, endDate);
saveLicenseToFile(license, `license_${customerId}.json`);
