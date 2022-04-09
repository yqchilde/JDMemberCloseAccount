.PHONY:  clean build

project=jd_wstool

# Builds the project
build:
		go build -o ${project}; \
		upx --best --lzma ${project}; \


release:
		# Clean
		go clean
		rm -rf *.gz

		# Build for mac with amd64
		CGO_ENABLED=0 GOOS=darwin GOARCH=amd64 GO111MODULE=on go build -ldflags="-s -w" -o ${project}; \
		upx --best --lzma ${project}; \
		tar -czvf ${project}-darwin-amd64.tar.gz ./${project}; \
		rm -rf ${project}; \

#		# Build for mac with arm64
		go clean
		CGO_ENABLED=0 GOOS=darwin GOARCH=arm64 GO111MODULE=on go build -ldflags="-s -w" -o ${project}; \
		tar czvf ${project}-darwin-arm64.tar.gz ./${project}; \
        rm -rf ${project}; \

#		# Build for linux with amd64
		go clean
		CGO_ENABLED=0 GOOS=linux GOARCH=amd64 GO111MODULE=on go build -ldflags="-s -w" -o ${project}; \
		upx --best --lzma ${project}; \
		tar czvf ${project}-linux-amd64.tar.gz ./${project}; \
		rm -rf ${project}; \

#		# Build for linux with arm
		go clean
		CGO_ENABLED=0 GOOS=linux GOARCH=arm GO111MODULE=on go build -ldflags="-s -w" -o ${project}; \
		upx --best --lzma ${project}; \
		tar czvf ${project}-linux-arm.tar.gz ./${project}; \
		rm -rf ${project}; \

		# Build for windows with amd64
		go clean
		CGO_ENABLED=0 GOOS=windows GOARCH=amd64 GO111MODULE=on go build -ldflags="-s -w" -o ${project}.exe; \
		upx --best --lzma ${project}.exe; \
		tar czvf ${project}-windows-amd64.tar.gz ./${project}.exe; \
		rm -rf ${project}.exe; \

		# Build for windows with 386
		go clean
		CGO_ENABLED=0 GOOS=windows GOARCH=386 GO111MODULE=on go build -ldflags="-s -w" -o ${project}.exe; \
		upx --best --lzma ${project}.exe; \
		tar czvf ${project}-windows-386.tar.gz ./${project}.exe; \
		rm -rf ${project}.exe; \

		# Build for windows with arm64
		go clean
		CGO_ENABLED=0 GOOS=windows GOARCH=arm64 GO111MODULE=on go build -ldflags="-s -w" -o ${project}.exe; \
		tar czvf ${project}-windows-arm64.tar.gz ./${project}.exe; \
		rm -rf ${project}.exe; \

		go clean

# Cleans our projects: deletes binaries
clean:
		rm -rf ${project}; \
		rm -rf ${project}.exe; \
		go clean
		rm -rf *.gz
