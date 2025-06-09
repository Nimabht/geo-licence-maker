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

  const licenseWithSignature = {
    ...license,
    signature,
  };

  return JSON.stringify(licenseWithSignature);
}

function saveLicenseToFile(license: string, filename: string) {
  fs.writeFileSync(filename, license);
}

const customerId = "oil";
const modules = ["module1", "module2"];
const startDate = "2025-06-01";
const endDate = "2025-12-31";

const license = generateLicense(customerId, modules, startDate, endDate);
saveLicenseToFile(license, `license_${customerId}.json`);
