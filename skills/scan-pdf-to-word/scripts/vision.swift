import Foundation
import Vision

let args = CommandLine.arguments
guard args.count == 4 else { fatalError("Usage: vision.swift manifest.json out languages") }
let manifestURL = URL(fileURLWithPath: args[1])
let outputURL = URL(fileURLWithPath: args[2], isDirectory: true)
let manifest = try JSONSerialization.jsonObject(with: Data(contentsOf: manifestURL)) as! [String: Any]
let pages = manifest["pages"] as! [[String: Any]]
for page in pages {
    let number = page["source_page"] as! Int
    let imageURL = manifestURL.deletingLastPathComponent().appendingPathComponent(page["image"] as! String)
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = args[3].split(separator: ",").map(String.init)
    request.usesLanguageCorrection = false
    request.minimumTextHeight = 0.003
    try VNImageRequestHandler(url: imageURL, options: [:]).perform([request])
    let regions: [[String: Any]] = (request.results ?? []).map { observation in
        let candidates = observation.topCandidates(3)
        let box = observation.boundingBox
        return ["text": candidates.first?.string ?? "", "confidence": candidates.first?.confidence ?? 0,
                "candidates": candidates.map { ["text": $0.string, "confidence": $0.confidence] as [String: Any] },
                "box": [box.minX, 1 - box.maxY, box.width, box.height]]
    }
    let record: [String: Any] = ["source_page": number, "engine": "vision", "regions": regions]
    let data = try JSONSerialization.data(withJSONObject: record, options: [.prettyPrinted, .sortedKeys])
    try data.write(to: outputURL.appendingPathComponent(String(format: "page-%04d.json", number)))
    print("OCR source page \(number): \(regions.count) regions")
}
