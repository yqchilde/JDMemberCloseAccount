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

		# Build for mac
		@for project in $$(ls cmd); \
		do \
			GO111MODULE=on go build "./cmd/$$project"; \
			upx "./$$project"; \
			tar czvf $$project-darwin-amd64.tar.gz ./$$project; \
		done

		# Build for linux
		go clean
		@for project in $$(ls cmd); \
		do \
			CGO_ENABLED=0 GOOS=linux GOARCH=amd64 GO111MODULE=on go build "./cmd/$$project"; \
			upx "./$$project"; \
			tar czvf $$project-linux-amd64.tar.gz ./$$project; \
		done

		# Build for windows
		go clean
		@for project in $$(ls cmd); \
		do \
			CGO_ENABLED=0 GOOS=windows GOARCH=amd64 GO111MODULE=on go build "./cmd/$$project"; \
			upx "./$$project".exe; \
			tar czvf $$project-windows-amd64.tar.gz ./$$project.exe; \
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
