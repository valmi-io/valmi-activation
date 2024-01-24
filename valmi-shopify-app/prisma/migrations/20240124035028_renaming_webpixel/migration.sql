/*
  Warnings:

  - You are about to drop the `webPixel` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropTable
PRAGMA foreign_keys=off;
DROP TABLE "webPixel";
PRAGMA foreign_keys=on;

-- CreateTable
CREATE TABLE "WebPixel" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "writeKey" TEXT NOT NULL
);
