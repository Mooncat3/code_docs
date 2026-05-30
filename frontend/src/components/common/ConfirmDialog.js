import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
} from "@mui/material";

const ConfirmDialog = ({
  open,
  onClose = () => {},
  onConfirm,
  title = "Подтвердить действие",
  message = "Вы уверены, что хотите выполнить это действие?",
}) => {
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        <DialogContentText>{message}</DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Отменить</Button>
        <Button onClick={onConfirm} color="error" variant="contained">
          Подтвердить
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ConfirmDialog;
