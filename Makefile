.PHONY:  clean build

# Builds the project
build:
		@for project in $$(ls cmd); \
		do \
			go build "./cmd/$$project"; \
			upx "./$$project"; \
		done


release:
		# Clean
		go clean
		rm -rf *.gz

		# Build for mac with amd64
		@for project in $$(ls cmd); \
		do \
			CGO_ENABLED=0 GOOS=darwin GOARCH=amd64 GO111MODULE=on go build "./cmd/$$project"; \
			upx "./$$project"; \
			tar czvf $$project-darwin-amd64.tar.gz ./$$project; \
		done

		# Build for mac with arm64
		@for project in $$(ls cmd); \
		do \
			CGO_ENABLED=0 GOOS=darwin GOARCH=arm64 GO111MODULE=on go build "./cmd/$$project"; \
			upx "./$$project"; \
			tar czvf $$project-darwin-arm64.tar.gz ./$$project; \
		done

		# Build for linux with amd64
		go clean
		@for project in $$(ls cmd); \
		do \
			CGO_ENABLED=0 GOOS=linux GOARCH=amd64 GO111MODULE=on go build "./cmd/$$project"; \
			upx "./$$project"; \
			tar czvf $$project-linux-amd64.tar.gz ./$$project; \
		done

		# Build for linux with arm
		go clean
		@for project in $$(ls cmd); \
		do \
			CGO_ENABLED=0 GOOS=linux GOARCH=arm GO111MODULE=on go build "./cmd/$$project"; \
			upx "./$$project"; \
			tar czvf $$project-linux-arm.tar.gz ./$$project; \
		done

		# Build for windows with amd64
		go clean
		@for project in $$(ls cmd); \
		do \
			CGO_ENABLED=0 GOOS=windows GOARCH=amd64 GO111MODULE=on go build "./cmd/$$project"; \
			upx "./$$project".exe; \
			tar czvf $$project-windows-amd64.tar.gz ./$$project.exe; \
		done

		# Build for windows with 386
		go clean
		@for project in $$(ls cmd); \
		do \
			CGO_ENABLED=0 GOOS=windows GOARCH=386 GO111MODULE=on go build "./cmd/$$project"; \
			upx "./$$project".exe; \
			tar czvf $$project-windows-386.tar.gz ./$$project.exe; \
		done

		go clean

# Cleans our projects: deletes binaries
clean:
		@for project in $$(ls cmd); \
		do \
			rm -rf $$project; \
			rm -rf $$project.exe; \
		done
		go clean
		rm -rf *.gz
