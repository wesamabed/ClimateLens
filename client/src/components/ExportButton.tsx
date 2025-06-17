import React, { useState } from "react";
import {
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
} from "@mui/material";
import {
  FileDownload,
  Description,
  DataObject,
  Schedule,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import { exportChat, ExportOptions } from "../utils/export";
import { Message } from "../App";
import styles from "./ExportButton.module.css";

interface ExportButtonProps {
  messages: Message[];
  disabled?: boolean;
}

const ExportButton: React.FC<ExportButtonProps> = ({
  messages,
  disabled = false,
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleExport = (options: ExportOptions) => {
    exportChat(messages, options);
    handleClose();
  };

  const isEmpty = messages.length === 0;

  return (
    <>
      <Tooltip title={isEmpty ? "No messages to export" : "Export chat"}>
        <span>
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <IconButton
              onClick={handleClick}
              disabled={disabled || isEmpty}
              className={styles.exportButton}
              aria-label="Export chat options"
              aria-expanded={open ? "true" : undefined}
              aria-haspopup="true"
            >
              <FileDownload />
            </IconButton>
          </motion.div>
        </span>
      </Tooltip>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        onClick={handleClose}
        PaperProps={{
          elevation: 8,
          sx: {
            backgroundColor: "var(--bg-primary)",
            border: "1px solid var(--border-color)",
            "& .MuiMenuItem-root": {
              color: "var(--text-primary)",
              "&:hover": {
                backgroundColor: "var(--primary-color-alpha)",
              },
            },
          },
        }}
        transformOrigin={{ horizontal: "right", vertical: "top" }}
        anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
      >
        <MenuItem
          onClick={() => handleExport({ format: "txt" })}
          className={styles.menuItem}
        >
          <ListItemIcon>
            <Description className={styles.menuIcon} />
          </ListItemIcon>
          <ListItemText
            primary="Export as Text"
            secondary="Simple text format"
          />
        </MenuItem>

        <MenuItem
          onClick={() =>
            handleExport({ format: "txt", includeTimestamps: true })
          }
          className={styles.menuItem}
        >
          <ListItemIcon>
            <Schedule className={styles.menuIcon} />
          </ListItemIcon>
          <ListItemText
            primary="Text with Timestamps"
            secondary="Include message times"
          />
        </MenuItem>

        <MenuItem
          onClick={() =>
            handleExport({
              format: "txt",
              includeTimestamps: true,
              includeSources: true,
            })
          }
          className={styles.menuItem}
        >
          <ListItemIcon>
            <Description className={styles.menuIcon} />
          </ListItemIcon>
          <ListItemText
            primary="Full Text Export"
            secondary="With timestamps & sources"
          />
        </MenuItem>

        <MenuItem
          onClick={() => handleExport({ format: "json" })}
          className={styles.menuItem}
        >
          <ListItemIcon>
            <DataObject className={styles.menuIcon} />
          </ListItemIcon>
          <ListItemText primary="Export as JSON" secondary="Raw data format" />
        </MenuItem>
      </Menu>
    </>
  );
};

export default ExportButton;
