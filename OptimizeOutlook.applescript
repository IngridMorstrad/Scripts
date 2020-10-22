set messagesToProcess to 10000 -- upper limit per folder
set progressInterval to 100 -- intervals at which to log progress
set deleteThreshold to 300
set nextCheckpoint to progressInterval
set folderNameToClean to "MyFolder"
global seenMessageIDs

tell application "Microsoft Outlook"
	repeat with currFolder in mail folders
		-- uncomment the next line to get folder names
		--log (name of currFolder as string)
		if name of currFolder as string = folderNameToClean then
			--log ("Starting cleanup of " & (name of currFolder))
			set messagesProcessed to 0
			set repeatsFound to 0
			
			set lastTimeReceived to current date
			
			repeat while messagesProcessed < messagesToProcess
				
				set toDelete to {}
				set seenMessageIDs to {}
				set msgs to messages of currFolder
				repeat with msg in msgs
					if msg's time received < lastTimeReceived then
						set messagesProcessed to messagesProcessed + 1
						set lastTimeReceived to msg's time received
						
						set refs to msg's headers as text
						set messageID to do shell script "awk -F 'Message-ID:|References:' '{print $2}'<<<" & (quoted form of refs)
						
						set hasReferences to (refs contains "References:")
						if hasReferences then
							set referenced to do shell script "awk -F 'Message-ID:|References:|In-Reply-To:|Accept-Language:' '{print $3}'<<<" & (quoted form of refs)
							set mailIdsReferenced to my split(my replaceNewlines(referenced, ""), "<", ">")
						end if
						set messageID to my split(my replaceNewlines(messageID, ""), "<", ">") as text
						-- Following may be useful later
						--set threadID to do shell script "awk -F 'Thread-Index:|Date:' '{print $2}'<<<" & (quoted form of refs)
						set doesNotHaveAttachments to ((msg's source as text) does not contain "Content-disposition: attachment")
						if seenMessageIDs does not contain messageID then
							if hasReferences then
								copy messageID to end of seenMessageIDs
								repeat with msgID in mailIdsReferenced
									copy msgID as text to end of seenMessageIDs
								end repeat
							end if
						else
							if doesNotHaveAttachments then
								copy msg to end of toDelete
							end if
						end if
						if messagesProcessed = nextCheckpoint then
							log ("Messages processed: " & messagesProcessed)
							log ("Messages to delete: " & (count of toDelete))
							-- set nextCheckpoint to the next progressInterval above messagesProcessed
							set nextCheckpoint to (((messagesProcessed - messagesProcessed mod progressInterval) / progressInterval + 1) * progressInterval)
						end if
						
						if (count of toDelete) > deleteThreshold or messagesProcessed > messagesToProcess then
							exit repeat -- exit and delete the duplicates, then continue
						end if
					else
						-- if it is the first time this loop is running
						if repeatsFound = 0 then
							log ("Message out-of-order" & msg's subject)
						end if
					end if
				end repeat
				
				set repeatsFound to (repeatsFound + (count of toDelete))
				my deleteMessages(toDelete)
				
				log ("Processed till: " & lastTimeReceived)
			end repeat
		end if
	end repeat
	log ("Processed " & messagesProcessed & " messages")
	log ((repeatsFound as text) & " repeats found & deleted")
end tell

on deleteMessages(toDelete)
	log ("Attempting to delete " & ((count of toDelete) as text) & " messages")
	repeat with msg in toDelete
		--log ("deleting message with id " & msg's id)
		delete msg
	end repeat
end deleteMessages

-- Creates a list, splitting on startDelim, endDelim
on split(inputStr, startDelim, endDelim)
	set currStr to ""
	set retList to {}
	repeat with i from 1 to count of inputStr
		if item i of inputStr = startDelim then
			set currStr to ""
		else if item i of inputStr = endDelim then
			copy currStr to end of retList
			set currStr to ""
		else
			set currStr to currStr & item i of inputStr
		end if
	end repeat
	return retList
end split

on replaceNewlines(this_text, replacement_string)
	set savedTextItemDelimiters to AppleScript's text item delimiters
	set AppleScript's text item delimiters to {return & linefeed, " ", return, linefeed, character id 8233, character id 8232}
	set newText to text items of this_text
	set AppleScript's text item delimiters to replacement_string
	set AppleScript's text item delimiters to savedTextItemDelimiters
	return newText as string
end replaceNewlines
