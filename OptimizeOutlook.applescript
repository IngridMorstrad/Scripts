global toDelete
set toDelete to {}
set messagesToProcess to 10000 -- upper limit per folder
set progressInterval to 100 -- intervals at which to log progress
set nextCheckpoint to progressInterval
set folderNameToClean to "MyFolder"

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
			set toContinue to true
			repeat while toContinue
				set toContinue to false
				set msgs to messages of currFolder
				-- TODO: Try partitioning messages by conversations and then processing each conversation
				repeat with msg in msgs
					set currSubj to subject of msg as string
					set truncatedSubject to my getTruncatedSubject(currSubj)
					set messagesProcessed to messagesProcessed + 1
					if seenMessageSubjects does not contain truncatedSubject then
						set toContinue to true -- there are more messages to process as we may exit early
						--log ("New master message for cleanup: " & currSubj)
						copy truncatedSubject to the end of seenMessageSubjects
						set relatedMails to (messages of currFolder whose subject contains truncatedSubject)
						set messagesProcessed to messagesProcessed + (count of relatedMails)
						set mailsToCleanup to my sortList(relatedMails)
						-- decrement as otherwise the parent message may be double counted
						set messagesProcessed to messagesProcessed - 1
						if my cleanupMessages(mailsToCleanup) then
							set cleanupCount to cleanupCount + 1
						end if
						
						-- optimized to exit only after a certain number of duplicates were found
						if cleanupCount > 50 then
							set cleanupCount to 0
							exit repeat -- exit and delete the duplicates, then continue
						end if
					end if
					if messagesProcessed ? nextCheckpoint then
						log ("Processed " & messagesProcessed & " messages")
						-- set nextCheckpoint to the next progressInterval above messagesProcessed
						set nextCheckpoint to (((messagesProcessed - messagesProcessed mod progressInterval) / progressInterval + 1) * progressInterval)
					end if
				end repeat
				set repeatsFound to (repeatsFound + (count of toDelete))
				repeat with msg in toDelete
					log ("deleting message") -- with id " & msg's exchange id)
					-- TODO: See if we can just delete the message when found
					delete msg
				end repeat
				if messagesProcessed > messagesToProcess then
					log ("Exiting")
					exit repeat
				end if
				set toDelete to {}
			end repeat
		end if
	end repeat
	log (repeatsFound & " repeats found & deleted")
end tell

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
	set foundDuplicates to false
	using terms from application "Microsoft Outlook"
		set allMessages to ""
		repeat with msg in msgs
			set ptc to plain text content of msg
			set ptcCleaned to my replaceNewlines(ptc, "")
			-- TODO: write a contains algorithm that ignores whitespace
			if allMessages contains ptcCleaned then
				copy msg to the end of toDelete
				set foundDuplicates to true
				log ("repeat found") -- & msg's exchange id)
			else
				set allMessages to allMessages & ptcCleaned
			end if
		end repeat
	end using terms from
	return foundDuplicates
end cleanupMessages

on replaceNewlines(this_text, replacement_string)
	set AppleScript's text item delimiters to {return & linefeed, " ", return, linefeed, character id 8233, character id 8232}
	set newText to text items of this_text
	set AppleScript's text item delimiters to replacement_string
	return newText as string
