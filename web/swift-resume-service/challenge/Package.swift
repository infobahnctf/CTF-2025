// swift-tools-version:6.0
import PackageDescription

let package = Package(
    name: "resume",
    platforms: [
       .macOS(.v13)
    ],
    dependencies: [
        // 💧 A server-side Swift web framework.
        .package(url: "https://github.com/vapor/vapor.git", from: "4.115.0"),
        // 🔵 Non-blocking, event-driven networking for Swift. Used for custom executors
        .package(url: "https://github.com/apple/swift-nio.git", from: "2.65.0"),
	.package(url: "https://github.com/vapor/leaf.git", from: "4.4.0"),
	.package(url: "https://github.com/scinfu/SwiftSoup.git", from: "2.11.1"),
    ],
    targets: [
        .executableTarget(
            name: "resume",
            dependencies: [
                .product(name: "Vapor", package: "vapor"),
                .product(name: "NIOCore", package: "swift-nio"),
                .product(name: "NIOPosix", package: "swift-nio"),
		.product(name: "Leaf", package: "leaf"),
		.product(name: "SwiftSoup", package: "SwiftSoup"),
            ],
            swiftSettings: swiftSettings
        ),
        .testTarget(
            name: "resumeTests",
            dependencies: [
                .target(name: "resume"),
                .product(name: "VaporTesting", package: "vapor"),
            ],
            swiftSettings: swiftSettings
        )
    ]
)

var swiftSettings: [SwiftSetting] { [
    .enableUpcomingFeature("ExistentialAny"),
] }
