set messagesToProcess to 10000 -- upper limit per folder
set progressInterval to 100 -- intervals at which to log progress
set nextCheckpoint to progressInterval
set folderNameToClean to "MyFolder"
global seenMessageIDs

tell application "Microsoft Outlook"
	repeat with currFolder in mail folders
		-- uncomment the next line to get folder names
		--log (name of currFolder as string)
		if name of currFolder as string = folderNameToClean then
			--log ("Starting cleanup of " & (name of currFolder))
			set currSubj to ""
			set cleanupCount to 0
			set messagesProcessed to 0
			set repeatsFound to 0
			set seenMessageSubjects to {}
			set seenMessageIDs to {}
			set toContinue to true
			set toDelete to {}
			repeat while toContinue
				set toContinue to false
				set msgs to messages of currFolder
				-- TODO: Try partitioning messages by conversations and then processing each conversation
				repeat with msg in msgs
					set currSubj to subject of msg as string
					set truncatedSubject to my getTruncatedSubject(currSubj)
					set messagesProcessed to messagesProcessed + 1
					set refs to msg's headers as text
					set messageID to do shell script "awk -F 'Message-ID:|References:|Accept-Language:' '{print $2}'<<<" & (quoted form of refs)
					set messageID to my split(my replaceNewlines(messageID, ""), "<", ">") as text
					if seenMessageIDs does not contain messageID then
						set toContinue to true -- there are more messages to process as we may exit early
						--log ("New master message for cleanup: " & currSubj)
						-- TODO: This could be changed to doing a DFS/BFS on the IDs in the reference section of the header. As it stands the code finds a larger list of related mails than is true (as the only requirement is that the truncated subject be contained).
						set relatedMails to (messages of currFolder whose subject contains truncatedSubject)
						set messagesProcessed to messagesProcessed + (count of relatedMails)
						set mailsToCleanup to my sortList(relatedMails)
						-- decrement as otherwise the parent message may be double counted
						set messagesProcessed to messagesProcessed - 1
						set newToDelete to my cleanupMessages(mailsToCleanup)
						repeat with msg in newToDelete
							copy msg to end of toDelete
						end repeat
						if (count of toDelete) > 0 then
							set cleanupCount to cleanupCount + 1
						end if
						-- optimized to exit only after a certain number of duplicates were found
						if cleanupCount > 50 then
							set cleanupCount to 0
							exit repeat -- exit and delete the duplicates, then continue
						end if
					end if
					if messagesProcessed = nextCheckpoint then
						log ("Processed " & messagesProcessed & " messages")
						-- set nextCheckpoint to the next progressInterval above messagesProcessed
						set nextCheckpoint to (((messagesProcessed - messagesProcessed mod progressInterval) / progressInterval + 1) * progressInterval)
					end if
				end repeat
				set repeatsFound to (repeatsFound + (count of toDelete))
				my deleteMessages(toDelete)
				if messagesProcessed > messagesToProcess then
					log ("Exiting")
					exit repeat
				end if
				-- TODO: Fix to subtract the messages that were not deleted from messages processed (as they will get processed again)
				set toDelete to {}
			end repeat
		end if
	end repeat
	log ((repeatsFound as text) & " repeats found & deleted")
end tell

on deleteMessages(toDelete)
	log ("deleting " & ((count of toDelete) as text) & " messages")
	repeat with msg in toDelete
		--log ("deleting message with id " & msg's id)
		delete msg
	end repeat
end deleteMessages

on sortList(myList)
	-- TODO: quick optimization: use a different sort (Tim Sort)
	using terms from application "Microsoft Outlook"
		repeat with i from 1 to (count of myList) - 1
			repeat with j from i + 1 to count of myList
				if time sent of item j of myList > time sent of item i of myList then
					set temp to item i of myList
					set item i of myList to item j of myList
					set item j of myList to temp
				end if
			end repeat
		end repeat
		return myList
	end using terms from
end sortList

on getTruncatedSubject(subject)
	set startLength to 1
	set endLength to 4
	set subjectLength to length of subject
	if subjectLength < startLength then
		set startLength to subjectLength
	end if
	if subjectLength < endLength then
		set endLength to subjectLength
	end if
	set truncatedSubject to text startLength thru endLength of subject
	if truncatedSubject is equal to "Re: " or truncatedSubject is equal to "Fw: " then
		set truncatedSubject to text 5 thru -1 of subject
	else
		set truncatedSubject to subject
	end if
	return truncatedSubject
end getTruncatedSubject

on cleanupMessages(msgs)
	set toDelete to {}
	set attachmentsSeen to {}
	using terms from application "Microsoft Outlook"
		repeat with msg in msgs
			set noAttachment to true
			set atts to msg's attachments
			repeat with att in atts
				-- TODO: Find a better way to determine unique attachments. Is there an attachment ID?
				if attachmentsSeen does not contain (att's name as text) then
					set noAttachment to false
					copy (att's name as text) to the end of attachmentsSeen
				end if
			end repeat
			--log ("Message with subject " & msg's subject & " has no attachment: " & noAttachment)
			set refs to msg's headers as text
			--log (refs)
			set messageID to do shell script "awk -F 'Message-ID:|References:|Accept-Language:' '{print $2}'<<<" & (quoted form of refs)
			set messageID to my split(my replaceNewlines(messageID, ""), "<", ">") as text
			--log ("current msg id: " & messageID)
			set messagesEnclosed to do shell script "awk -F 'In-Reply-To:|Reply-To:|References:' '{print $2}'<<<" & (quoted form of refs)
			set messagesEnclosed to my split(my replaceNewlines(messagesEnclosed, ""), "<", ">")
			--log ("The messages enclosed were: " & messagesEnclosed)
			if noAttachment then
				if seenMessageIDs contains messageID then
					copy msg to the end of toDelete
					--log ("sending message ID: " & messageID & " to be deleted") -- & msg's exchange id)
				end if
			end if
			if seenMessageIDs does not contain messageID then
				copy (messageID as text) to the end of seenMessageIDs
				
				repeat with messageEnclosed in messagesEnclosed
					if seenMessageIDs does not contain messageEnclosed then
						copy (messageEnclosed as text) to the end of seenMessageIDs
					end if
				end repeat
			end if
		end repeat
	end using terms from
	return toDelete
end cleanupMessages

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
